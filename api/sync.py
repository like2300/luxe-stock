"""Synchronisation hors ligne (voir docs/SYNC.md).

Trois garanties tiennent l'ensemble :

1. **Le stock n'est jamais écrit directement.** Un `create` ou `update` de
   produit ignore `quantity` : seul un mouvement (`record_movement`) ou un
   ajustement (`record_adjustment`) modifie la quantité. C'est la seule façon
   d'éviter qu'une quantité absolue érifiée écrase le stock réel.
2. **Le push est idempotent.** Chaque `op_id` est journalisé avec la réponse
   renvoyée ; un rejeu du même `op_id` ne touche rien et rend la même réponse.
3. **Le curseur est composite** (`updated_at`, `id`) et par entité : deux lignes
   modifiées dans la même microseconde ne peuvent pas en sauter une.
"""

import base64
import json
import uuid as uuid_lib
from decimal import Decimal, InvalidOperation as DecimalInvalidOperation

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.forms import clean_image_upload
from core.models import (
    Category,
    Membership,
    Notification,
    Product,
    Profile,
    Shop,
    StockMovement,
    push_notification,
    record_adjustment,
    record_movement,
)

from . import schema
from . import serializers as s
from .exceptions import RejectedOperation
from .models import SyncOperation
from .payloads import category_payload, membership_payload, profile_payload, shop_payload
from .permissions import IsShopMember, ShopScopedMixin

CURSOR_VERSION = 1

# 500 lignes par entité et par appel : assez pour rattrapager un mois de
# saisie hors ligne sans.noyer la base locale d'un coup.
PULL_LIMIT = 500
# 200 opérations par push : au-delà, la réponse devient ingérable pour l'app.
PUSH_LIMIT = 200

CURSOR_ENTITIES = (
    "shop",
    "category",
    "product",
    "movement",
    "notification",
    "membership",
    "profile",
)

PERMANENT_HINT = "Les opérations rejetées restent dans la file jusqu'à correction ou abandon."


# ==========================================================================
# Curseur
# ==========================================================================
def _mark(value):
    return None if value is None else {"ts": value[0].isoformat(), "id": value[1]}


def encode_cursor(marks):
    """Transforme des marques par entité en une seule chaîne opaque."""
    payload = {"v": CURSOR_VERSION, "e": {name: _mark(marks.get(name)) for name in CURSOR_ENTITIES}}
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(raw):
    """Relit un curseur. Une valeur illisible est une erreur franche.

    On ne devine jamais : mieux vaut une erreur explicite qui déclenche un
    téléchargement complet qu'un curseur mal interprete qui perdrait des lignes.
    """
    try:
        padded = raw + "=" * (-len(raw) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        if data.get("v") != CURSOR_VERSION:
            raise ValueError("version inconnue")
        entities = data["e"]
        marks = {}
        for name in CURSOR_ENTITIES:
            entry = entities.get(name)
            if not entry:
                marks[name] = None
                continue
            ts = parse_datetime(entry["ts"])
            if ts is None:
                raise ValueError("horodatage illisible")
            if timezone.is_naive(ts):
                ts = timezone.make_aware(ts)
            marks[name] = (ts, int(entry["id"]))
        return marks
    except RejectedOperation:
        raise
    except Exception:
        raise ValidationError(
            {
                "cursor": [
                    "Curseur de synchronisation invalide. "
                    "Relancez un téléchargement complet."
                ]
            }
        )


def _after(qs, mark):
    """Lignes modifiées strictement apres la marque (ou les lignes d'identifiant
    supérieur having la même horodatage)."""
    if mark:
        ts, last_id = mark
        qs = qs.filter(Q(updated_at__gt=ts) | Q(updated_at=ts, id__gt=last_id))
    return qs.order_by("updated_at", "id")


def _page(qs, mark, limit=PULL_LIMIT):
    rows = list(_after(qs, mark)[: limit + 1])
    truncated = len(rows) > limit
    rows = rows[:limit]
    new_mark = (rows[-1].updated_at, rows[-1].id) if rows else mark
    return rows, new_mark, truncated


# ==========================================================================
# Pull
# ==========================================================================
class SyncPullView(ShopScopedMixin, IsShopMember, APIView):
    """Téléchargement des changements depuis le curseur du client.

    Le pull est strictement en lecture : il ne touche jamais au stock.
    """

    throttle_scope = "pull"

    @extend_schema(
        tags=["Synchronisation"],
        summary="Télécharger les changements",
        description="Sans curseur : téléchargement initial complet. Avec curseur : "
                    "incrémental strict. Les lignes supprimées logiquement sont "
                    "incluses (deleted_at renseigné).",
        parameters=[
            OpenApiParameter("cursor", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, OpenApiParameter.QUERY,
                description=f"Lignes maximum par entité (1 à {PULL_LIMIT}, défaut {PULL_LIMIT}).",
            ),
        ],
        responses={200: schema.SyncPullSchema, 400: schema.ErrorSchema},
    )
    def get(self, request):
        shop, membership = self.shop, self.membership
        raw = request.query_params.get("cursor", "")
        marks = decode_cursor(raw) if raw else {name: None for name in CURSOR_ENTITIES}
        # Le parametre `limit` existe pour la reprise apres troncature : on le
        # borne, et une valeur illisible retombe sur le defaut plutot que 400.
        page_size = _int(request.query_params.get("limit"), PULL_LIMIT)
        page_size = max(1, min(page_size, PULL_LIMIT))

        body, new_marks, truncated_flags = {}, {}, {}

        # Boutique : une seule ligne, renvoyee si elle a change depuis le curseur.
        rows, mark, cut = _page(Shop.objects.filter(pk=shop.pk), marks["shop"], limit=1)
        body["shop"] = shop_payload(rows[-1]) if rows else None
        new_marks["shop"], truncated_flags["shop"] = mark, cut

        categories, mark, cut = _page(
            Category.all_objects.filter(shop=shop).annotate(
                # Le compteur ignore les produits supprimes logiquement.
                product_count=Count("products", filter=Q(products__deleted_at__isnull=True))
            ),
            marks["category"],
            limit=page_size,
        )
        body["categories"] = [category_payload(c) for c in categories]
        new_marks["category"], truncated_flags["category"] = mark, cut

        products, mark, cut = _page(
            Product.all_objects.filter(shop=shop).select_related("category"),
            marks["product"],
            limit=page_size,
        )
        body["products"] = [s.ProductSerializer(p).data for p in products]
        new_marks["product"], truncated_flags["product"] = mark, cut

        movements, mark, cut = _page(
            StockMovement.all_objects.filter(product__shop=shop).select_related(
                "product", "user"
            ),
            marks["movement"],
            limit=page_size,
        )
        body["movements"] = [s.MovementSerializer(m).data for m in movements]
        new_marks["movement"], truncated_flags["movement"] = mark, cut

        notifications, mark, cut = _page(
            Notification.all_objects.filter(shop=shop).select_related("product", "user"),
            marks["notification"],
            limit=page_size,
        )
        body["notifications"] = [s.NotificationSerializer(n).data for n in notifications]
        new_marks["notification"], truncated_flags["notification"] = mark, cut

        # Adhesions : le proprietaire seul recoit la liste complete (elle contient
        # les permissions des comptes). Un employe ne recoit que la sienne.
        memberships_qs = Membership.objects.filter(shop=shop).select_related("user")
        if not membership.is_owner:
            memberships_qs = memberships_qs.filter(pk=membership.pk)
        memberships, mark, cut = _page(memberships_qs, marks["membership"], limit=page_size)
        body["memberships"] = [membership_payload(m) for m in memberships]
        new_marks["membership"], truncated_flags["membership"] = mark, cut

        profiles, mark, cut = _page(
            Profile.objects.filter(user=request.user), marks["profile"], limit=1
        )
        body["profile"] = profile_payload(request.user, membership)
        new_marks["profile"] = mark if profiles else marks["profile"]

        return Response(
            {
                "cursor": encode_cursor(new_marks),
                "has_more": any(truncated_flags.values()),
                "truncated": truncated_flags,
                "counts": {name: len(body[key]) for name, key in _BODY_KEYS.items()},
                **body,
                "server_time": timezone.now(),
            }
        )


_BODY_KEYS = {
    "category": "categories",
    "product": "products",
    "movement": "movements",
    "notification": "notifications",
    "membership": "memberships",
}


# ==========================================================================
# Push
# ==========================================================================
class _Context:
    """Tout ce dont un gestionnaire d'operation a besoin."""

    def __init__(self, request, membership):
        self.request = request
        self.user = request.user
        self.membership = membership
        self.shop = membership.shop

    def require(self, permission):
        if not self.membership.has(permission):
            raise RejectedOperation(
                "permission_denied",
                "Vous n'avez pas la permission de modifier cette donnée.",
                {"action": "contact_owner"},
            )

    def require_owner(self):
        if not self.membership.is_owner:
            raise RejectedOperation(
                "permission_denied",
                "Vous n'avez pas la permission de modifier cette donnée.",
                {"action": "contact_owner"},
            )


class SyncPushView(ShopScopedMixin, IsShopMember, APIView):
    """Applique un lot d'opérations hors ligne, une par une.

    Chaque opération est indépendante : un rejet n'annule pas les autres, et la
    réponse conserve l'ordre d'envoi pour que le client puisse faire correspondre
    résultat et opération de sa file.
    """

    throttle_scope = "push"

    @extend_schema(
        tags=["Synchronisation"],
        summary="Envoyer les opérations hors ligne",
        description="Lot idempotent : rejouer un op_id ne modifie rien et rend la "
                    "même réponse. 200 opérations maximum par appel.",
        request=s.SyncPushRequestSerializer,
        responses={200: schema.SyncPushSchema, 400: schema.ErrorSchema},
    )
    def post(self, request):
        data = request.data or {}
        device_id = str(data.get("device_id") or "")[:64]
        operations = data.get("operations")

        if not isinstance(operations, list) or not operations:
            # Un lot vide est un bug de file cote client : repondre 200 ferait
            # croire que tout a ete synchronise alors que rien n'a ete lu.
            return Response(
                {
                    "detail": "Liste d'opérations attendue.",
                    "reason_code": "bad_payload",
                    "suggestion": {"action": "retry"},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(operations) > PUSH_LIMIT:
            return Response(
                {
                    "detail": f"Lot trop volumineux : {PUSH_LIMIT} opérations maximum.",
                    "reason_code": "batch_too_large",
                    "suggestion": {"action": "retry"},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ctx = _Context(request, self.membership)
        results = [_process(ctx, op, device_id) for op in operations]

        return Response(
            {
                "results": results,
                "applied": sum(1 for r in results if r["status"] == SyncOperation.APPLIED),
                "with_warning": sum(
                    1 for r in results if r["status"] == SyncOperation.APPLIED_WITH_WARNING
                ),
                "rejected": sum(1 for r in results if r["status"] == SyncOperation.REJECTED),
                "server_time": timezone.now(),
            }
        )


def _process(ctx, op, device_id):
    """Applique une operation, en reusing une réponse déjà journalisee."""
    if not isinstance(op, dict):
        return _result(None, SyncOperation.REJECTED, reason_code="bad_payload",
                       reason="Opération illisible.", suggestion={"action": "discard"})

    raw_op_id = op.get("op_id")
    try:
        op_id = uuid_lib.UUID(str(raw_op_id))
    except (ValueError, TypeError, AttributeError):
        return _result(None, SyncOperation.REJECTED, reason_code="bad_payload",
                       reason="Identifiant d'opération manquant ou invalide.",
                       suggestion={"action": "discard"})

    # Idempotence : un op_id deja traite rend exactement la meme reponse.
    journal = SyncOperation.objects.filter(user=ctx.user, op_id=op_id).first()
    if journal is not None:
        replay = dict(journal.result or {})
        replay["replayed"] = True
        return replay

    op_type = str(op.get("type") or "")
    entity = str(op.get("entity") or "")
    payload = op.get("payload")
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return _finish(ctx, op_id, op_type, entity, SyncOperation.REJECTED,
                       reason_code="bad_payload",
                       reason="Charge utile illisible : un objet était attendu.",
                       suggestion={"action": "discard"}, payload=payload, device_id=device_id)

    try:
        result = _dispatch(ctx, op_type, entity, op, payload)
    except RejectedOperation as exc:
        result = _result(op_id, SyncOperation.REJECTED, entity=entity, uuid=_row_uuid(op),
                         reason_code=exc.reason_code, reason=exc.reason,
                         suggestion=exc.suggestion)
    except DjangoValidationError as exc:
        result = _result(op_id, SyncOperation.REJECTED, entity=entity, uuid=_row_uuid(op),
                         reason_code="invalid_field", reason=_first_message(exc),
                         suggestion={"action": "retry"})
    except ValidationError as exc:
        result = _result(op_id, SyncOperation.REJECTED, entity=entity, uuid=_row_uuid(op),
                         reason_code="invalid_field", reason=_first_message(exc),
                         suggestion={"action": "retry"})
    except Exception as exc:  # pragma: no cover - filet de securite
        result = _result(op_id, SyncOperation.REJECTED, entity=entity, uuid=_row_uuid(op),
                         reason_code="bad_payload", reason=str(exc)[:200],
                         suggestion={"action": "retry"})

    status_name = result.get("status")
    _finish(ctx, op_id, op_type, entity, status_name,
            **{k: v for k, v in result.items()
               if k in ("uuid", "server", "warning", "reason_code", "reason",
                        "suggestion", "adjustment")},
            payload=payload, device_id=device_id, result=result)
    return result


def _finish(ctx, op_id, op_type, entity, status_name, uuid=None, server=None, warning=None,
            reason_code="", reason="", suggestion=None, adjustment=None, payload=None,
            device_id="", result=None):
    """Journalise l'operation pour rendre la reponse rejouable."""
    response = result if result is not None else _result(
        op_id, status_name, entity=entity, uuid=uuid, server=server, warning=warning,
        reason_code=reason_code, reason=reason, suggestion=suggestion,
        adjustment=adjustment,
    )
    SyncOperation.objects.create(
        op_id=op_id,
        user=ctx.user,
        entity=entity[:20],
        op_type=op_type[:24],
        status=status_name,
        reason_code=reason_code[:32],
        reason=reason[:250],
        result=response,
        payload=payload if isinstance(payload, dict) else {},
        device_id=device_id[:64],
    )
    return response


def _result(op_id, status_name, entity=None, uuid=None, server=None, warning=None,
            reason_code=None, reason=None, suggestion=None, adjustment=None):
    """Réponse d'une opération : même forme pour un succès et pour un refus."""
    data = {"op_id": str(op_id), "status": status_name}
    if entity:
        data["entity"] = entity
    if uuid:
        data["uuid"] = str(uuid)
    if server is not None:
        data["server"] = server
    if warning:
        data["warning"] = warning
    if adjustment is not None:
        data["adjustment"] = adjustment
    if reason_code:
        data["reason_code"] = reason_code
        data["reason"] = reason
        data["suggestion"] = suggestion or {}
    return data


def _row_uuid(op):
    raw = (op or {}).get("uuid")
    try:
        return uuid_lib.UUID(str(raw))
    except (ValueError, TypeError, AttributeError):
        return None


def _first_message(exc):
    if hasattr(exc, "message_dict"):
        for messages in exc.message_dict.values():
            if messages:
                return str(messages[0])
    if hasattr(exc, "messages") and exc.messages:
        return str(exc.messages[0])
    return str(exc)


def _client_time(op):
    value = parse_datetime(str(op.get("client_time") or ""))
    if value is None:
        return None
    return timezone.make_aware(value) if timezone.is_naive(value) else value


# ==========================================================================
# Aiguillage
# ==========================================================================
def _dispatch(ctx, op_type, entity, op, payload):
    handlers = {
        ("create", "product"): _op_product_create,
        ("update", "product"): _op_product_update,
        ("delete", "product"): _op_product_delete,
        ("create", "category"): _op_category_create,
        ("update", "category"): _op_category_update,
        ("delete", "category"): _op_category_delete,
        ("movement", "movement"): _op_movement,
        ("adjust", "movement"): _op_adjust,
        ("notification_read", "notification"): _op_notification_read,
        ("notification_read_all", "notification"): _op_notification_read_all,
        ("notification_clear", "notification"): _op_notification_clear,
        ("update", "shop"): _op_shop_update,
        ("update", "profile"): _op_profile_update,
        ("update", "membership"): _op_membership_update,
        ("delete", "membership"): _op_membership_delete,
    }
    handler = handlers.get((op_type, entity))
    if handler is None:
        raise RejectedOperation(
            "bad_payload",
            f"Opération non prise en charge : {op_type} / {entity}.",
            {"action": "discard"},
        )
    return handler(ctx, op, payload)


# ==========================================================================
# Produits
# ==========================================================================
PRODUCT_TEXT_FIELDS = {"name": 150, "sku": 40, "barcode": 64, "description": 10000}


def _op_product_create(ctx, op, payload):
    ctx.require("can_add_products")
    shop = ctx.shop

    name = str(payload.get("name") or "").strip()
    if not name:
        raise RejectedOperation(
            "invalid_field", "Champ « Nom du produit » : Ce champ est obligatoire.",
            {"field": "name", "action": "retry"},
        )

    category_ref = payload.get("category")
    category = _resolve_category(shop, category_ref)
    if category_ref and category is None:
        # Reference inexistante dans CETTE boutique : ne pas creer le produit
        # sans categorie en silence, l'app croirait avoir reussi.
        raise RejectedOperation(
            "not_found",
            "Cette catégorie n'existe pas dans cette boutique.",
            {"field": "category", "action": "choose_other"},
        )
    sku = str(payload.get("sku") or "").strip()[:40]
    if sku and shop.products.filter(sku=sku).exists():
        raise RejectedOperation("duplicate_sku", "Cette référence existe déjà.",
                                {"field": "sku", "action": "choose_other"})
    barcode = "".join(str(payload.get("barcode") or "").split())[:64]
    if barcode and shop.products.filter(barcode=barcode).exists():
        raise RejectedOperation(
            "duplicate_barcode",
            f"Le code-barres {barcode} est déjà attribué à un autre produit "
            "de cette boutique.",
            {"field": "barcode", "action": "choose_other"},
        )

    with transaction.atomic():
        product = Product(
            shop=shop,
            name=name[:150],
            category=category,
            sku=sku,
            barcode=barcode,
            cost_price=_decimal(payload.get("cost_price"), 0),
            sale_price=_decimal(payload.get("sale_price"), 0),
            alert_threshold=_positive_int(payload.get("alert_threshold"), 5),
            description=str(payload.get("description") or "")[:10000],
        )
        row_uuid = _row_uuid(op)
        if row_uuid is not None:
            product.uuid = row_uuid
        # Regle 1 : la quantite envoyee est ignoree. Le client enfile un
        # mouvement juste apres, qui sera la seule source de verite du stock.
        product.save()

    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="product", uuid=product.uuid,
        server=s.ProductSerializer(product).data,
    )


def _op_product_update(ctx, op, payload):
    ctx.require("can_edit_products")
    product = _product(ctx.shop, op, live=True)
    if product is None:
        # Comme `delete` et `update` de categorie : une ligne absente est
        # rejetee, jamais creee implicitement. Sans ce garde, le dereferencement
        # plus bas leve une AttributeError, Attributes que le filet de securite
        # transformerait en `bad_payload` avec le message Python dans `reason`.
        gone = _product(ctx.shop, op, live=False)
        if gone is not None:
            raise RejectedOperation(
                "product_deleted",
                f"« {gone.name} » a été supprimé sur un autre appareil ; cette "
                "modification n'a pas pu être enregistrée.",
                {"action": "discard_or_create", "product": gone.name},
            )
        raise RejectedOperation(
            "not_found", "Ce produit n'existe pas sur le serveur.",
            {"action": "discard"},
        )

    # Regle 2 : dernier a ecrire gagne, compare champ par champ. Si la ligne a
    # ete modifiee apres l instant du client, le serveur l'emporte.
    client_time = _client_time(op)
    if client_time is not None and product.updated_at > client_time:
        return _result(
            _row_uuid(op), SyncOperation.APPLIED_WITH_WARNING, entity="product",
            uuid=product.uuid, server=s.ProductSerializer(product).data,
            warning=(
                "Champs non appliqués : ce produit a été modifié sur un autre "
                "appareil après votre dernière connexion. Les valeurs du serveur "
                "ont été conservées."
            ),
        )

    changed = []
    for field, length in PRODUCT_TEXT_FIELDS.items():
        if field in payload:
            value = str(payload[field] or "").strip()
            if field == "barcode":
                value = "".join(value.split())
            # Seuls sku et barcode sont uniques dans une boutique.
            if field in ("sku", "barcode"):
                _check_product_unique(ctx.shop, product, field, value)
            setattr(product, field, value[:length])
            changed.append(field)
    if "category" in payload:
        product.category = _resolve_category(ctx.shop, payload.get("category"))
        changed.append("category")
    for field in ("cost_price", "sale_price"):
        if field in payload:
            setattr(product, field, _decimal(payload[field], 0))
            changed.append(field)
    if "alert_threshold" in payload:
        product.alert_threshold = _positive_int(payload["alert_threshold"], 5)
        changed.append("alert_threshold")
    # Regle 1 : `quantity` n'est jamais applique ici.

    if changed:
        product.save()
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="product", uuid=product.uuid,
        server=s.ProductSerializer(product).data,
        warning=("Champs ignorés : la quantité. Le stock ne se modifie que par "
                 "un mouvement ou un ajustement.") if "quantity" in payload else None,
    )


def _op_product_delete(ctx, op, payload):
    ctx.require("can_delete_products")
    row_uuid = _row_uuid(op)
    product = _product(ctx.shop, op, live=True)
    if product is None:
        already = _product(ctx.shop, op, live=False)
        if already is not None:
            # Deja supprimee : l'operation n'a plus rien a faire.
            return _result(
                row_uuid, SyncOperation.APPLIED, entity="product", uuid=already.uuid,
                server=s.ProductSerializer(already).data,
                warning="Ce produit était déjà supprimé.",
            )
        raise RejectedOperation(
            "not_found", "Ce produit n'existe pas sur le serveur.",
            {"action": "discard"},
        )
    product.soft_delete()
    return _result(
        row_uuid, SyncOperation.APPLIED, entity="product", uuid=product.uuid,
        server=s.ProductSerializer(product).data,
    )


def _check_product_unique(shop, product, field, value):
    if not value:
        return
    qs = shop.products.filter(**{field: value})
    if product is not None and product.pk:
        qs = qs.exclude(pk=product.pk)
    if qs.exists():
        code, message = {
            "sku": ("duplicate_sku", "Cette référence existe déjà."),
            "barcode": (
                "duplicate_barcode",
                f"Le code-barres {value} est déjà attribué à un autre produit "
                "de cette boutique.",
            ),
        }[field]
        raise RejectedOperation(code, message, {"field": field, "action": "choose_other"})


# ==========================================================================
# Catégories
# ==========================================================================
def _op_category_create(ctx, op, payload):
    ctx.require("can_manage_categories")
    name = str(payload.get("name") or "").strip()
    if not name:
        raise RejectedOperation(
            "invalid_field", "Champ « Nom » : Ce champ est obligatoire.",
            {"field": "name", "action": "retry"},
        )
    if ctx.shop.categories.filter(name__iexact=name).exists():
        raise RejectedOperation("duplicate_category", "Cette catégorie existe déjà.",
                                {"field": "name", "action": "choose_other"})
    category = Category(shop=ctx.shop, name=name[:80])
    row_uuid = _row_uuid(op)
    if row_uuid is not None:
        category.uuid = row_uuid
    category.save()
    return _result(
        row_uuid, SyncOperation.APPLIED, entity="category", uuid=category.uuid,
        server=category_payload(category),
    )


def _op_category_update(ctx, op, payload):
    ctx.require("can_manage_categories")
    category = _category(ctx.shop, op, live=True)
    if category is None:
        raise RejectedOperation("not_found", "Cette catégorie n'existe pas sur le serveur.",
                                {"action": "discard"})
    if "name" in payload:
        name = str(payload["name"] or "").strip()[:80]
        if not name:
            raise RejectedOperation(
                "invalid_field", "Champ « Nom » : Ce champ est obligatoire.",
                {"field": "name", "action": "retry"},
            )
        qs = ctx.shop.categories.filter(name__iexact=name).exclude(pk=category.pk)
        if qs.exists():
            raise RejectedOperation("duplicate_category", "Cette catégorie existe déjà.",
                                    {"field": "name", "action": "choose_other"})
        category.name = name
        category.save()
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="category", uuid=category.uuid,
        server=category_payload(category),
    )


def _op_category_delete(ctx, op, payload):
    ctx.require("can_manage_categories")
    category = _category(ctx.shop, op, live=True)
    if category is None:
        raise RejectedOperation("not_found", "Cette catégorie n'existe pas sur le serveur.",
                                {"action": "discard"})
    now = timezone.now()
    # Comme le web (SET_NULL), les produits de la categorie redeviennent « sans
    # categorie » ; leur horodatage bouge pour que les autres appareils le voient.
    Product.objects.filter(category=category).update(category=None, updated_at=now)
    category.deleted_at = now
    category.save(update_fields=["deleted_at", "updated_at"])
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="category", uuid=category.uuid,
        server=category_payload(category),
    )


# ==========================================================================
# Mouvements (seul chemin qui modifie le stock)
# ==========================================================================
def _op_movement(ctx, op, payload):
    ctx.require("can_manage_stock")
    shop = ctx.shop
    product = _product(shop, op, live=False, from_payload=payload)
    if product is None:
        raise RejectedOperation("not_found", "Produit introuvable dans cette boutique.",
                                {"action": "discard"})
    if product.is_deleted:
        # Regle 4 : le produit a disparu pendant que l'app etait hors ligne.
        raise RejectedOperation(
            "product_deleted",
            f"« {product.name} » a été supprimé le "
            f"{timezone.localtime(product.deleted_at).strftime('%d/%m/%Y') if product.deleted_at else ''} "
            "sur un autre appareil ; ce mouvement n'a pas pu être enregistré.",
            {"action": "discard_or_create", "product": product.name},
        )

    kind = str(payload.get("kind") or "")
    if kind not in (StockMovement.IN, StockMovement.OUT):
        raise RejectedOperation("invalid_kind",
                                'Type de mouvement invalide : utilisez "IN" ou "OUT".',
                                {"action": "retry"})
    quantity = _int(payload.get("quantity"), default=0)
    if quantity < 1:
        raise RejectedOperation("invalid_quantity", "La quantité doit être au moins 1.",
                                {"field": "quantity", "action": "retry"})

    requested = quantity
    warning = None
    # Regle 3 : une sortie plus grande que le stock s'arrete a zero et le dit.
    if kind == StockMovement.OUT and quantity > product.quantity:
        if product.quantity <= 0:
            raise RejectedOperation(
                "invalid_quantity", "Stock insuffisant (disponible : 0).",
                {"field": "quantity", "action": "retry"},
            )
        quantity = product.quantity
        warning = (
            f"Stock ramené à 0 : la sortie de {requested} unités a dépassé le stock "
            f"disponible ({product.quantity})."
        )

    note = str(payload.get("note") or "")[:200]
    with transaction.atomic():
        record_movement(product, kind, quantity, note, ctx.user)
        product.refresh_from_db()
        push_notification(
            product,
            Notification.STOCK_IN if kind == StockMovement.IN else Notification.STOCK_OUT,
            user=ctx.user,
            message=f"{'Entrée' if kind == StockMovement.IN else 'Sortie'} de "
            f"{quantity} — {product.name} ({product.quantity} en stock)",
        )
        if warning:
            push_notification(
                product, Notification.ADJUSTED, user=ctx.user,
                message=f"Sortie limitée : {requested} demandées, {quantity} "
                        f"appliquées — {product.name} ({product.quantity} en stock)",
            )

    return _result(
        _row_uuid(op),
        SyncOperation.APPLIED_WITH_WARNING if warning else SyncOperation.APPLIED,
        entity="movement", uuid=_row_uuid(op),
        server={"product_uuid": str(product.uuid), "quantity": product.quantity},
        warning=warning,
        adjustment={"kind": kind, "requested": requested, "applied": quantity}
        if requested != quantity
        else None,
    )


def _op_adjust(ctx, op, payload):
    """Ecart de quantite saisi hors ligne : le serveur recalcule l'ecart.

    `previous_quantity` est la quantité que l'app voyait ; si le serveur a
    bouge entre-temps, le calcul se fait sur son propre etat et l'app est
    prevenue par un avertissement.
    """
    ctx.require("can_edit_products")
    product = _product(ctx.shop, op, live=False, from_payload=payload)
    if product is None:
        raise RejectedOperation("not_found", "Produit introuvable dans cette boutique.",
                                {"action": "discard"})
    if product.is_deleted:
        raise RejectedOperation(
            "product_deleted",
            f"« {product.name} » a été supprimé sur un autre appareil ; cet "
            "ajustement n'a pas pu être enregistré.",
            {"action": "discard_or_create", "product": product.name},
        )

    previous = _int(payload.get("previous_quantity"), default=product.quantity)
    target = max(0, _int(payload.get("quantity"), default=product.quantity))
    server_before = product.quantity
    warning = None
    if server_before != previous:
        warning = (
            f"Stock modifié entre-temps (serveur : {server_before}) : l'écart a été "
            "recalculé sur la valeur du serveur."
        )

    note = str(payload.get("note") or "Ajustement manuel")[:200]
    with transaction.atomic():
        product.quantity = target
        product.save(update_fields=["quantity", "updated_at"])
        # C'est `server_before` qui est historise, pas la quantite vue par l'app :
        # le mouvement doit tracer l'ecart reellement survenu sur le serveur.
        record_adjustment(product, server_before, ctx.user, note=note)
    product.refresh_from_db()

    return _result(
        _row_uuid(op),
        SyncOperation.APPLIED_WITH_WARNING if warning else SyncOperation.APPLIED,
        entity="movement", uuid=_row_uuid(op),
        server={"product_uuid": str(product.uuid), "quantity": product.quantity},
        warning=warning,
    )


# ==========================================================================
# Notifications
# ==========================================================================
def _op_notification_read(ctx, op, payload):
    ctx.require("can_view_products")
    row_uuid = _row_uuid(op)
    notification = ctx.shop.notifications.filter(uuid=row_uuid).first() if row_uuid else None
    if notification is None:
        raise RejectedOperation("not_found", "Cette notification n'existe pas sur le serveur.",
                                {"action": "discard"})
    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])
    return _result(
        row_uuid, SyncOperation.APPLIED, entity="notification", uuid=notification.uuid,
        server=s.NotificationSerializer(notification).data,
    )


def _op_notification_read_all(ctx, op, payload):
    ctx.require("can_view_products")
    count = ctx.shop.notifications.filter(is_read=False).update(
        is_read=True, updated_at=timezone.now()
    )
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="notification",
        server={"marked": count},
        warning=f"{count} notification(s) marquée(s) comme lue(s)." if count else None,
    )


def _op_notification_clear(ctx, op, payload):
    ctx.require("can_view_products")
    notifications = list(ctx.shop.notifications.all())
    for notification in notifications:
        notification.soft_delete()
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="notification",
        server={"cleared": len(notifications)},
        warning=f"{len(notifications)} notification(s) supprimée(s)."
        if notifications
        else None,
    )


# ==========================================================================
# Boutique, profil, employés
# ==========================================================================
SHOP_FIELDS = (
    "name", "address", "phone", "currency",
    "primary_color", "sidebar_color", "header_color", "background_color",
    "scanner_enabled", "barcode_field_enabled",
)
SHOP_COLOR_FIELDS = ("primary_color", "sidebar_color", "header_color", "background_color")
SHOP_BOOL_FIELDS = ("scanner_enabled", "barcode_field_enabled")

# Longueurs maximales lues sur le modele plutot que recopiees : un
# `max_length` change cote core ne peut pas laisser la validation de la
# synchronisation desynchronisee du schema reel des colonnes.
SHOP_FIELD_LIMITS = {
    name: Shop._meta.get_field(name).max_length
    for name in SHOP_FIELDS
    if getattr(Shop._meta.get_field(name), "max_length", None)
}

_TRUEY = {"1", "true", "t", "yes", "y", "on", "oui"}
_FALSEY = {"", "0", "false", "f", "no", "n", "off", "non"}


def _boolean(value, field):
    """Booléen lu depuis une charge utile JSON.

    Le push n'a pas de serializer DRF derriere lui : sans cette conversion,
    `setattr(shop, "scanner_enabled", "false")` ferait echouer `save()` sur une
    ValidationError, et le `create` du journal qui suit-la se heurterait alors a
    une transaction deja cassee — le lot entier remontait en 500 au lieu de
    rendre un refus lisible par operation.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value if value is not None else "").strip().lower()
    if text in _TRUEY:
        return True
    if text in _FALSEY:
        return False
    raise RejectedOperation(
        "invalid_field",
        f"Champ « {field} » : utilisez true ou false.",
        {"field": field, "action": "choose_other"},
    )


def _op_shop_update(ctx, op, payload):
    ctx.require_owner()
    shop = ctx.shop
    applied = []
    for field in SHOP_FIELDS:
        if field not in payload:
            continue
        value = payload[field]
        if field in SHOP_COLOR_FIELDS:
            value = str(value or "").strip()
            errors = Shop._meta.get_field(field).validators[0](value)
            if errors:
                raise RejectedOperation("invalid_field", f"Couleur {field} : {errors[0].messages[0]}",
                                        {"field": field, "action": "choose_other"})
        elif field in SHOP_BOOL_FIELDS:
            value = _boolean(value, field)
        else:
            # Comme pour les produits et les categories : on borne plutot que de
            # laisser la colonne deborder ( silencieux sur SQLite, refus sur
            # PostgreSQL). L'etat serveur renvoye permet au client de le voir.
            value = str(value or "").strip()[: SHOP_FIELD_LIMITS.get(field, 0)]
        if field == "name" and not value:
            raise RejectedOperation(
                "invalid_field", "Champ « Nom de la boutique » : Ce champ est obligatoire.",
                {"field": "name", "action": "retry"},
            )
        setattr(shop, field, value)
        applied.append(field)
    if applied:
        shop.save()
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="shop", uuid=shop.uuid,
        server=shop_payload(shop),
        warning=("Champs ignorés : " + ", ".join(sorted(set(payload) - set(applied))) + ".")
        if set(payload) - set(applied)
        else None,
    )


def _op_profile_update(ctx, op, payload):
    profile = Profile.objects.get_or_create(user=ctx.user)[0]
    applied = []
    if "phone" in payload:
        profile.phone = str(payload["phone"] or "")[:40]
        applied.append("phone")
    if "bio" in payload:
        profile.bio = str(payload["bio"] or "")[:200]
        applied.append("bio")
    if applied:
        profile.save()
    return _result(
        _row_uuid(op), SyncOperation.APPLIED, entity="profile", uuid=profile.uuid,
        server=profile_payload(ctx.user, ctx.membership),
    )


def _op_membership_update(ctx, op, payload):
    ctx.require_owner()
    row_uuid = _row_uuid(op)
    target = ctx.shop.members.filter(uuid=row_uuid).first() if row_uuid else None
    if target is None:
        raise RejectedOperation("not_found", "Cet employé n'existe pas sur le serveur.",
                                {"action": "discard"})
    if target.is_owner:
        raise RejectedOperation(
            "permission_denied", "Les permissions du propriétaire ne sont pas modifiables.",
            {"action": "contact_owner"},
        )
    from core.models import PERMISSIONS

    changed = []
    for name, _label in PERMISSIONS:
        if name in payload:
            setattr(target, name, bool(payload[name]))
            changed.append(name)
    if changed:
        target.save()
    return _result(
        row_uuid, SyncOperation.APPLIED, entity="membership", uuid=target.uuid,
        server=membership_payload(target),
    )


def _op_membership_delete(ctx, op, payload):
    ctx.require_owner()
    row_uuid = _row_uuid(op)
    target = ctx.shop.members.filter(uuid=row_uuid, is_owner=False).first() if row_uuid else None
    if target is None:
        raise RejectedOperation("not_found", "Cet employé n'existe pas sur le serveur.",
                                {"action": "discard"})
    target.user.delete()
    return _result(row_uuid, SyncOperation.APPLIED, entity="membership", uuid=row_uuid,
                   server={"deleted": True})


# ==========================================================================
# Aides de resolution
# ==========================================================================
def _product(shop, op, live=True, from_payload=None):
    """Produit par uuid d'operation, ou par reference dans la charge utile.

    Le filtre `shop` n'est jamais omis : une operation Id ou une reference
    venue d'un autre appareil ne doit pas pouvoir viser une autre boutique.
    """
    row_uuid = _row_uuid(op)
    manager = Product.objects if live else Product.all_objects
    product = (
        manager.filter(shop=shop, uuid=row_uuid).first() if row_uuid else None
    )
    if product is not None:
        return product
    if from_payload:
        reference = from_payload.get("product") or from_payload.get("product_uuid")
        if reference:
            return _resolve_product(shop, reference, live=live)
    return None


def _resolve_product(shop, reference, live=True):
    """Produit par uuid, identifiant, code-barres ou reference - jamais par nom."""
    manager = Product.objects if live else Product.all_objects
    manager = manager.filter(shop=shop)
    try:
        parsed = uuid_lib.UUID(str(reference))
    except (ValueError, TypeError, AttributeError):
        parsed = None
    if parsed is not None:
        return manager.filter(uuid=parsed).first()
    text = str(reference)
    if text.isdigit():
        return manager.filter(pk=int(text)).first()
    normalized = "".join(text.split())
    return manager.filter(barcode=normalized).first() or manager.filter(sku=text).first()


def _category(shop, op, live=True):
    row_uuid = _row_uuid(op)
    manager = Category.objects if live else Category.all_objects
    return manager.filter(shop=shop, uuid=row_uuid).first() if row_uuid else None


def _resolve_category(shop, reference):
    if reference in (None, ""):
        return None
    try:
        parsed = uuid_lib.UUID(str(reference))
    except (ValueError, TypeError, AttributeError):
        parsed = None
    if parsed is not None:
        return shop.categories.filter(uuid=parsed).first()
    text = str(reference)
    if text.isdigit():
        return shop.categories.filter(pk=int(text)).first()
    return shop.categories.filter(name__iexact=text).first()


def _decimal(value, default=0):
    try:
        return Decimal(str(value))
    except (DecimalInvalidOperation, TypeError, ValueError):
        return Decimal(str(default))


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _positive_int(value, default=0):
    return max(0, _int(value, default))


# ==========================================================================
# Photos (appel multipart separe)
# ==========================================================================
class SyncPhotoView(ShopScopedMixin, IsShopMember, APIView):
    """Envoi d'un fichier image, dans un appel distinct du lot de donnees.

    Un binaire qui echoue ne doit pas faire perdre les operations de donnees
    deja acceptees : d'ou la separation.
    """

    throttle_scope = "push"
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = s.PhotoUploadSerializer

    @extend_schema(
        tags=["Synchronisation"],
        summary="Envoyer une image",
        description="Appel multipart distinct du lot de données : un binaire qui "
                    "échoue ne doit pas faire perdre les opérations déjà acceptées.",
        request=s.PhotoUploadSerializer,
        responses={200: schema.SyncPhotoSchema, 400: schema.ErrorSchema},
    )
    def post(self, request):
        entity = str(request.data.get("entity") or "profile")
        upload = request.FILES.get("file") or request.FILES.get("photo") or request.FILES.get("logo")

        if entity == "shop":
            ctx = _Context(request, self.membership)
            ctx.require_owner()
            upload = clean_image_upload(
                upload, max_bytes=2 * 1024 * 1024, max_label="2 Mo",
                allowed_types={"image/png", "image/jpeg", "image/webp"},
                formats_label="JPEG, PNG ou WebP", field_label="Logo",
            )
            if upload is not None:
                self.shop.logo = upload
                self.shop.save(update_fields=["logo", "updated_at"])
            return Response({"entity": "shop", "server": shop_payload(self.shop)})

        if entity != "profile":
            return Response(
                {"detail": "Entité non prise en charge : utilisez « profile » ou « shop ».",
                 "reason_code": "bad_payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = Profile.objects.get_or_create(user=request.user)[0]
        upload = clean_image_upload(
            upload, max_bytes=2 * 1024 * 1024, max_label="2 Mo",
            allowed_types={"image/jpeg", "image/png", "image/webp", "image/gif"},
            formats_label="JPEG, PNG, WebP ou GIF", field_label="Photo",
        )
        if upload is not None:
            profile.photo = upload
            profile.save(update_fields=["photo", "updated_at"])
        return Response(
            {
                "entity": "profile",
                "server": profile_payload(request.user, self.membership),
                "detail": "Profil mis à jour.",
            }
        )


# ==========================================================================
# Etat et journal
# ==========================================================================
class SyncStatusView(ShopScopedMixin, IsShopMember, APIView):
    """Sonde d'atteinte du serveur et etat de la file du client."""

    throttle_scope = "pull"

    @extend_schema(
        tags=["Synchronisation"],
        summary="État du serveur",
        description="Sonde d'atteinte : c'est cette route que l'application "
                    "interroge pour distinguer « hors ligne » de « serveur injoignable ».",
        responses={200: schema.SyncStatusSchema},
    )
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "shop_uuid": str(self.shop.uuid),
                "shop_name": self.shop.name,
                "server_time": timezone.now(),
                "unread_count": self.shop.notifications.filter(is_read=False).count(),
                "rejected_count": SyncOperation.objects.filter(
                    user=request.user, status=SyncOperation.REJECTED
                ).count(),
                "last_cursor": request.query_params.get("cursor", "")[:400],
            }
        )


class SyncOperationsView(ShopScopedMixin, IsShopMember, APIView):
    """Journal des operations : l'ecran « Synchronisation » s'en sert pour
    expliquer les refus et proposer une correction."""

    @extend_schema(
        tags=["Synchronisation"],
        summary="Journal des opérations",
        parameters=[
            OpenApiParameter("status", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             enum=["applied", "applied_with_warning", "rejected"]),
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses={200: schema.SyncOperationsSchema},
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 50) or 50)
        except (TypeError, ValueError):
            limit = 50
        # Borne basse obligatoire : `ops[:-1]` est une indexation negative, que
        # Django refuse d'executer (ValueError) — le journal devenait un 500.
        limit = max(1, min(limit, 200))
        ops = SyncOperation.objects.filter(user=request.user)
        only = request.query_params.get("status", "")
        if only in (SyncOperation.REJECTED, SyncOperation.APPLIED, SyncOperation.APPLIED_WITH_WARNING):
            ops = ops.filter(status=only)
        rows = [
            {
                "op_id": str(op.op_id),
                "entity": op.entity,
                "type": op.op_type,
                "status": op.status,
                "reason_code": op.reason_code,
                "reason": op.reason,
                "device_id": op.device_id,
                "created_at": op.created_at,
            }
            for op in ops[:limit]
        ]
        return Response({"count": len(rows), "results": rows, "hint": PERMANENT_HINT})