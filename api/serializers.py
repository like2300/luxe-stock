"""Serialiseurs de l'API.

Principe : les messages d'erreur sont ceux des formulaires du web, sans les
réécrire. Quand c'est possible, le formulaire lui-même est appelé
(`SignupForm`, `clean_image_upload`) ou son validateur (`hex_color`,
`validate_password`) : il n'y a donc pas deux listes de messages à maintenir.
"""

from decimal import Decimal
from decimal import InvalidOperation as DecimalInvalidOperation

import uuid as uuid_lib
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.avatar import avatar_data, ensure_profile
from core.forms import SignupForm, clean_image_upload
from core.models import (
    PERMISSIONS,
    Category,
    Membership,
    Notification,
    Product,
    Shop,
    StockMovement,
    push_notification,
    record_adjustment,
    record_movement,
)
from core.templatetags.core_tags import LEVEL_LABELS

from .permissions import get_membership


def _as_int(value, default=0):
    """Quantites : les clients hors ligne envoient parfois des chaines."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def resolve_product(shop, reference):
    """Produit de la boutique par uuid, identifiant, code-barres ou reference.

    Utilise par les champs a plat comme par le lot de scan, qui doit pouvoir
    dire « Ligne N : produit introuvable ».
    """
    if reference in (None, ""):
        return None
    try:
        parsed = uuid_lib.UUID(str(reference))
    except (ValueError, TypeError, AttributeError):
        parsed = None
    products = shop.products
    if parsed is not None:
        return products.filter(uuid=parsed).first()
    text = str(reference)
    # Le code-barres passe avant l'identifiant : un code a 8 a 14 chiffres ne
    # doit pas etre lu comme un `pk`, et le web recherche le code en premier.
    normalized = "".join(text.split())
    by_code = products.filter(barcode=normalized).first()
    if by_code is not None:
        return by_code
    if text.isdigit():
        return products.filter(pk=int(text)).first()
    return products.filter(sku=text).first()


# --------------------------------------------------------------------------
# Résolution des liens entre entités
# --------------------------------------------------------------------------
@extend_schema_field(serializers.UUIDField(allow_null=True))
class CategoryRefField(serializers.Field):
    """Catégorie référencée par uuid, identifiant ou nom.

    L'autocomplétion du web transmet un identifiant ; la synchronisation
    transmet un uuid ; les signets ou un client minimal utilisent le nom. Les
    trois sont acceptés, toujours dans la boutique du membre.
    """

    default_error_messages = {
        "not_found": "Cette catégorie n'existe pas dans cette boutique.",
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("allow_null", True)
        super().__init__(**kwargs)

    def to_representation(self, value) -> str | None:
        return str(value.uuid) if value else None

    def to_internal_value(self, data):
        if data in (None, ""):
            return None
        shop = self.context["shop"]
        text = str(data).strip()
        try:
            parsed = uuid_lib.UUID(text)
        except (ValueError, AttributeError, TypeError):
            parsed = None
        if parsed is not None:
            category = shop.categories.filter(uuid=parsed).first()
        elif text.isdigit():
            category = shop.categories.filter(pk=int(text)).first()
        else:
            category = shop.categories.filter(name__iexact=text).first()
        if category is None:
            raise serializers.ValidationError(self.error_messages["not_found"])
        return category


@extend_schema_field(serializers.UUIDField(allow_null=True))
class ProductRefField(serializers.Field):
    """Produit référencé par uuid, identifiant, code-barres ou référence.

    Jamais par nom : deux produits peuvent porter le même nom, et une sortie de
    stock ne doit jamais se tromper de cible.
    """

    default_error_messages = {
        "not_found": "Produit introuvable dans cette boutique.",
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(**kwargs)

    def to_representation(self, value) -> str | None:
        return str(value.uuid) if value else None

    def to_internal_value(self, data):
        if data in (None, ""):
            return None
        product = resolve_product(self.context["shop"], str(data).strip())
        if product is None:
            raise serializers.ValidationError(self.error_messages["not_found"])
        return product


# --------------------------------------------------------------------------
# Compte
# --------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    # Message unique du web : « Veuillez entrer un nom d'utilisateur et un mot
    # de passe corrects. », volontairement identique pour un identifiant inconnu
    # et pour un mot de passe erroné.
    default_error_messages = {
        "invalid": "Veuillez entrer un nom d'utilisateur et un mot de passe corrects."
    }

    def validate(self, attrs):
        from django.contrib.auth import authenticate

        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {"detail": self.error_messages["invalid"]}, code="invalid"
            )
        attrs["user"] = user
        return attrs


class SignupSerializer(serializers.Serializer):
    """Inscription : mêmes champs et mêmes messages que `SignupForm`."""

    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=60, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password1 = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        form = SignupForm(
            data={
                "username": attrs.get("username", ""),
                "first_name": attrs.get("first_name", ""),
                "email": attrs.get("email", ""),
                "password1": attrs.get("password1", ""),
                "password2": attrs.get("password2", ""),
            }
        )
        if not form.is_valid():
            # Les libellés du formulaire sont déjà en français (LANGUAGE_CODE).
            raise serializers.ValidationError(
                {field: list(errors) for field, errors in form.errors.items()}
            )
        attrs["user"] = form.save()
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Mot de passe d'un compte employé (« Laisser vide pour ne pas changer. »)."""

    password = serializers.CharField(required=False, allow_blank=True, trim_whitespace=False)

    def validate_password(self, value):
        user = self.context.get("user")
        if value:
            validate_password(value, user)
        return value


class LogoutSerializer(serializers.Serializer):
    """Deconnexion : le jeton de rafraichissement a mettre en liste noire.

    Le jeton est obligatoire : sans lui, la deconnexion repondrait « succes »
    alors qu'aucune session n'a ete revoquee.
    """

    refresh = serializers.CharField(trim_whitespace=False)


# ---------- Synchronisation ----------
class SyncOperationSerializer(serializers.Serializer):
    """Une operation de la file hors ligne.

    `op_id` est genere par le client et fait office d'identifiant d'idempotence
    (docs/SYNC.md § 4.3) : un rejeu rend la meme reponse sans rien modifier.
    """

    op_id = serializers.UUIDField()
    type = serializers.CharField(max_length=24)
    entity = serializers.CharField(max_length=20)
    uuid = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.DictField(required=False)
    client_time = serializers.DateTimeField(required=False, allow_null=True)


class SyncPushRequestSerializer(serializers.Serializer):
    """Lot d'operations envoye au push."""

    device_id = serializers.CharField(required=False, allow_blank=True, max_length=64)
    # `allow_empty=False` : un lot vide est un bug du client, pas une
    # synchronisation reussie. Repondre 200 ferait disparaitre des operations.
    operations = SyncOperationSerializer(many=True, allow_empty=False)


class PhotoUploadSerializer(serializers.Serializer):
    """Envoi d'une image : appel multipart distinct du lot de donnees."""

    entity = serializers.ChoiceField(
        choices=["profile", "shop"], required=False, default="profile"
    )
    file = serializers.ImageField(required=False, allow_null=True)


# --------------------------------------------------------------------------
# Boutique
# --------------------------------------------------------------------------
class ShopSerializer(serializers.ModelSerializer):
    initials = serializers.CharField(read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            "uuid", "name", "address", "phone", "currency",
            "primary_color", "sidebar_color", "header_color", "background_color",
            "scanner_enabled", "barcode_field_enabled",
            "initials", "logo_url",
        ]
        read_only_fields = ["uuid"]

    def get_logo_url(self, obj) -> str | None:
        return obj.logo.url if obj.logo else None


class ShopCreateSerializer(serializers.ModelSerializer):
    """Création de boutique : mêmes champs et mêmes couleurs par défaut."""

    class Meta:
        model = Shop
        fields = [
            "uuid", "name", "address", "phone", "currency", "logo",
            "primary_color", "sidebar_color", "header_color", "background_color",
        ]
        extra_kwargs = {
            "address": {"required": False},
            "phone": {"required": False},
            "logo": {"required": False},
            # Les quatre couleurs ont une valeur par defaut : un client qui ne les
            # envoie pas ne doit pas etre refuse (cf. ShopCreateForm.clean).
            "primary_color": {"required": False},
            "sidebar_color": {"required": False},
            "header_color": {"required": False},
            "background_color": {"required": False},
        }
        read_only_fields = ["uuid"]

    def create(self, validated_data):
        defaults = {
            name: Shop._meta.get_field(name).default
            for name in ("primary_color", "sidebar_color", "header_color", "background_color")
        }
        for field, value in defaults.items():
            validated_data.setdefault(field, value)
        return super().create(validated_data)


class ShopSettingsFormLimits:
    """Plafonds repris de `core.forms.ShopSettingsForm`."""

    FAVICON_BYTES = 256 * 1024
    FAVICON_TYPES = {"image/png", "image/jpeg", "image/x-icon", "image/vnd.microsoft.icon"}


class ShopSettingsSerializer(serializers.Serializer):
    """Paramètres de la boutique : identité, thème, fonctionnalités.

    Aucun champ n'est obligatoire : l'écran de paramètres n'envoie que ce qu'il
    a modifié, et une valeur manquante ne doit pas effacer la donnée en base.
    Le thème est fusionné champ par champ : le client ne renvoie que les
    couleurs qu'il a changées.
    """

    name = serializers.CharField(max_length=120, required=False)
    address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=10, required=False)
    logo = serializers.ImageField(required=False, allow_null=True)
    favicon = serializers.ImageField(required=False, allow_null=True)
    favicon_remove = serializers.BooleanField(required=False, write_only=True)
    scanner_enabled = serializers.BooleanField(required=False)
    barcode_field_enabled = serializers.BooleanField(required=False)
    primary_color = serializers.CharField(required=False)
    sidebar_color = serializers.CharField(required=False)
    header_color = serializers.CharField(required=False)
    background_color = serializers.CharField(required=False)

    COLORS = ("primary_color", "sidebar_color", "header_color", "background_color")

    def validate(self, attrs):
        # Meme validateur que le formulaire : « Couleur invalide (format #rrggbb). »
        errors = {}
        for field in self.COLORS:
            if field in attrs:
                for error in Shop._meta.get_field(field).validators[0](attrs[field]):
                    errors[field] = error.messages[0]
        # Interrupteurs dessines a la main par le web : absents = desactives.
        for field in ("scanner_enabled", "barcode_field_enabled"):
            if field not in attrs:
                attrs[field] = False
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def validate_logo(self, value):
        return clean_image_upload(
            value,
            max_bytes=2 * 1024 * 1024,
            max_label="2 Mo",
            allowed_types={"image/png", "image/jpeg", "image/webp"},
            formats_label="JPEG, PNG ou WebP",
            field_label="Logo",
        )

    def validate_favicon(self, value):
        # Meme plafond que ShopSettingsForm : le favicon est recharge a chaque onglet.
        return clean_image_upload(
            value,
            max_bytes=ShopSettingsFormLimits.FAVICON_BYTES,
            max_label="256 Ko",
            allowed_types=ShopSettingsFormLimits.FAVICON_TYPES,
            formats_label="PNG, JPEG ou ICO",
            field_label="Icône du site",
        )

    def save_shop(self, shop):
        data = self.validated_data
        if data.pop("favicon_remove", False) and shop.favicon:
            shop.favicon.delete(save=False)
        for field, value in data.items():
            setattr(shop, field, value)
        shop.save()
        return shop


# --------------------------------------------------------------------------
# Catégories
# --------------------------------------------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["uuid", "name", "product_count", "updated_at", "deleted_at"]
        read_only_fields = ["uuid", "product_count", "updated_at", "deleted_at"]

    def validate_name(self, value):
        # Le web teste l'unicite « sans distinction de casse » (iexact).
        shop = self.context["shop"]
        qs = shop.categories.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Cette catégorie existe déjà.")
        return value.strip()


# --------------------------------------------------------------------------
# Produits
# --------------------------------------------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategoryRefField()
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    level = serializers.CharField(read_only=True)
    level_label = serializers.SerializerMethodField()
    is_low = serializers.BooleanField(read_only=True)
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "uuid", "name", "sku", "barcode", "category", "category_name",
            "cost_price", "sale_price", "quantity", "alert_threshold",
            "description", "level", "level_label", "is_low", "currency",
            "created_at", "updated_at", "deleted_at",
        ]
        read_only_fields = [
            "uuid", "level", "level_label", "is_low",
            "currency", "created_at", "updated_at", "deleted_at",
        ]
        extra_kwargs = {
            "description": {"required": False, "allow_blank": True},
        }

    def get_currency(self, obj) -> str:
        return obj.shop.currency

    def get_level_label(self, obj) -> str:
        return LEVEL_LABELS.get(obj.level, obj.level)

    # -- validations reprises de core.forms.ProductForm ---------------------
    def validate_sku(self, value):
        sku = (value or "").strip()
        if sku:
            qs = self.context["shop"].products.filter(sku=sku)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Cette référence existe déjà.")
        return sku

    def validate_barcode(self, value):
        # Meme normalisation que Product.save() : l'unicite porte sur la valeur
        # reellement enregistree.
        barcode = "".join((value or "").split())
        if barcode:
            qs = self.context["shop"].products.filter(barcode=barcode)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Le code-barres {barcode} est déjà attribué à un autre produit "
                    "de cette boutique."
                )
        return barcode

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("La quantité ne peut pas être négative.")
        return value

    # -- creation : mouvement « Stock initial » + notification -------------
    def create(self, validated_data):
        quantity = max(0, _as_int(validated_data.pop("quantity", 0)))
        shop = self.context["shop"]
        user = self.context["request"].user
        with transaction.atomic():
            # Le produit demarre a zero : le stock initial passe par
            # `record_movement()` comme n'importe quelle entree, sinon le
            # mouvements et l'historique nestories pas la meme chose.
            product = Product.objects.create(shop=shop, **validated_data)
            if quantity > 0:
                record_movement(product, StockMovement.IN, quantity, "Stock initial", user)
            push_notification(product, Notification.PRODUCT_ADDED, user=user)
        return product

    # -- modification : ecart trace par record_adjustment() ---------------
    def update(self, instance, validated_data):
        user = self.context["request"].user
        # La quantite precedente doit etre lue AVANT toute ecriture : c'est
        # l'ecart a historiser que `record_adjustment()` recalcule.
        before = instance.quantity
        requested_quantity = validated_data.pop("quantity", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if requested_quantity is not None:
            target = max(0, _as_int(requested_quantity))
            if target != before:
                with transaction.atomic():
                    instance.quantity = target
                    instance.save(update_fields=["quantity", "updated_at"])
                    record_adjustment(instance, before, user)
                instance.refresh_from_db()
        return instance


class ProductListSerializer(ProductSerializer):
    """Version legere de la liste : pas de description."""

    class Meta(ProductSerializer.Meta):
        fields = [
            "uuid", "name", "sku", "barcode", "category", "category_name",
            "cost_price", "sale_price", "quantity", "alert_threshold",
            "level", "level_label", "is_low", "currency",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "uuid", "quantity", "level", "level_label", "is_low", "currency",
            "created_at", "updated_at",
        ]


# --------------------------------------------------------------------------
# Mouvements
# --------------------------------------------------------------------------
class MovementSerializer(serializers.ModelSerializer):
    product = ProductRefField()
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True, default=None)

    class Meta:
        model = StockMovement
        fields = [
            "uuid", "product", "product_name", "product_sku", "kind", "kind_label",
            "quantity", "note", "username", "created_at", "updated_at", "deleted_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at", "deleted_at"]

    def validate_kind(self, value):
        if value not in (StockMovement.IN, StockMovement.OUT):
            raise serializers.ValidationError(
                'Type de mouvement invalide : utilisez "IN" ou "OUT".'
            )
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La quantité doit être au moins 1.")
        return value

    def validate(self, attrs):
        product = attrs.get("product")
        if product is None:
            raise serializers.ValidationError({"product": "Choisissez un produit."})
        if attrs.get("kind") == StockMovement.OUT and attrs["quantity"] > product.quantity:
            raise serializers.ValidationError(
                {"quantity": f"Stock insuffisant (disponible : {product.quantity})."}
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data.pop("product")
        kind = validated_data["kind"]
        quantity = validated_data["quantity"]
        note = validated_data.get("note", "")
        # record_movement() est la reference unique du recalcul de stock.
        movement = record_movement(product, kind, quantity, note, user)
        product.refresh_from_db()
        push_notification(
            product,
            Notification.STOCK_IN if kind == StockMovement.IN else Notification.STOCK_OUT,
            user=user,
            message=f"{'Entrée' if kind == StockMovement.IN else 'Sortie'} de "
            f"{quantity} — {product.name} ({product.quantity} en stock)",
        )
        return movement


class ScanLineSerializer(serializers.Serializer):
    """Une ligne de lot scanné.

    Le produit est résolu par le lot (`validate`), pas ligne par ligne, pour
    pouvoir répondre « Ligne N : … » comme le web.
    """

    # `product` accepte uuid / identifiant / code-barres / référence ; `code` est
    # l'alias naturel pour une saisie scanner.
    product = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La quantité doit être au moins 1.")
        return value


class ScanBatchSerializer(serializers.Serializer):
    """Lot scanné. Atomique : si une ligne est refusée, rien n'est enregistré."""

    kind = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True, max_length=200)
    items = ScanLineSerializer(many=True)

    default_error_messages = {
        "kind": 'Type de mouvement invalide : utilisez "IN" ou "OUT".',
        "empty": "Aucune ligne à enregistrer.",
    }

    def validate_kind(self, value):
        if value not in (StockMovement.IN, StockMovement.OUT):
            raise serializers.ValidationError(self.error_messages["kind"])
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(self.error_messages["empty"])
        return value

    def validate(self, attrs):
        shop = self.context["shop"]
        errors = []
        for index, line in enumerate(attrs["items"], start=1):
            reference = line.get("product") or line.get("code")
            product = resolve_product(shop, reference)
            if product is None:
                errors.append(f"Ligne {index} : produit introuvable dans cette boutique.")
                continue
            line["product_obj"] = product
            quantity = line["quantity"]
            if attrs["kind"] == StockMovement.OUT and quantity > product.quantity:
                errors.append(
                    f"Ligne {index} — {product.name} : stock insuffisant "
                    f"(disponible : {product.quantity})."
                )
        if errors:
            # Liste de messages : le web affiche exactement ces lignes.
            raise serializers.ValidationError({"lines": errors})
        return attrs

    def save_batch(self):
        user = self.context["request"].user
        kind = self.validated_data["kind"]
        note = self.validated_data.get("note", "")
        is_in = kind == StockMovement.IN
        summary = []
        with transaction.atomic():
            for line in self.validated_data["items"]:
                product, quantity = line["product_obj"], line["quantity"]
                record_movement(product, kind, quantity, note, user)
                product.refresh_from_db()
                push_notification(
                    product,
                    Notification.STOCK_IN if is_in else Notification.STOCK_OUT,
                    user=user,
                    message=f"{'Entrée' if is_in else 'Sortie'} de {quantity} — "
                    f"{product.name} ({product.quantity} en stock)",
                )
                summary.append(
                    {
                        "uuid": str(product.uuid),
                        "name": product.name,
                        "quantity": quantity,
                        "stock": product.quantity,
                        "level": product.level,
                    }
                )
        return summary


# --------------------------------------------------------------------------
# Notifications
# --------------------------------------------------------------------------
class NotificationSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="label", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True, default=None)
    username = serializers.CharField(source="user.username", read_only=True, default=None)
    colors = serializers.SerializerMethodField()
    tone = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "uuid", "kind", "kind_label", "message", "product_name",
            "quantity", "alert_threshold", "sound_code", "level", "colors",
            "tone", "is_read", "username", "created_at", "updated_at", "deleted_at",
        ]
        read_only_fields = fields

    def get_colors(self, obj) -> list[str]:
        # (fond, texte) : les deux valeurs d'origine de LEVEL_COLORS, que le
        # client applique sans les recalculer.
        return list(obj.colors)


# --------------------------------------------------------------------------
# Employés
# --------------------------------------------------------------------------
def permission_fields():
    """Les six cases de permissions de `core.forms.EmployeeForm`."""
    return {
        name: serializers.BooleanField(required=False, label=label)
        for name, label in PERMISSIONS
    }


class EmployeeSerializer(serializers.Serializer):
    """Employé : identité, permissions accordées, rôle."""

    uuid = serializers.UUIDField(read_only=True)
    username = serializers.CharField(max_length=150, required=False)
    initials = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(max_length=60, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=60, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    role = serializers.SerializerMethodField()
    granted_permissions = serializers.SerializerMethodField()
    # Chaine et non sous-serie : la vue fait `user.set_password(...)`, et
    # « Laisser vide pour ne pas changer. » est la regle du web.
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True, trim_whitespace=False
    )
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Les six cases de permissions existent aussi en modification : sans
        # elles, le proprietaire ne pourrait pas les changer.
        for name, field in permission_fields().items():
            self.fields[name] = field

    def validate_password(self, value):
        if value:
            validate_password(value, self.context.get("employee"))
        return value

    def get_initials(self, obj) -> str:
        # Le web prend les deux premieres lettres du nom d'utilisateur.
        return (obj.get_username() or "?")[:2].upper()

    def get_role(self, obj) -> str:
        return "Employé"

    def get_granted_permissions(self, obj) -> list[str]:
        membership = getattr(obj, "membership", None)
        if membership is None:
            return []
        return [label for name, label in PERMISSIONS if membership.has(name)]

    def validate_username(self, value):
        qs = User.objects.filter(username__iexact=value)
        user = self.context.get("employee")
        if user is not None:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value


class EmployeeCreateSerializer(EmployeeSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in permission_fields().items():
            self.fields[name] = field

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Le mot de passe est obligatoire.")
        validate_password(value)
        return value

    def create(self, validated_data):
        permissions = {
            name: validated_data.pop(name, False) for name, _label in PERMISSIONS
        }
        password = validated_data.pop("password")
        with transaction.atomic():
            user = User.objects.create_user(
                password=password,
                username=validated_data.pop("username"),
                first_name=validated_data.pop("first_name", ""),
                last_name=validated_data.pop("last_name", ""),
                email=validated_data.pop("email", ""),
            )
            # can_view_products est cochee par defaut dans le formulaire web.
            permissions["can_view_products"] = True
            membership = Membership.objects.create(
                user=user, shop=self.context["shop"], **permissions
            )
        user.membership = membership
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        membership = getattr(instance, "membership", None)
        if membership is not None:
            data["uuid"] = str(membership.uuid)
            data["granted_permissions"] = [
                label for name, label in PERMISSIONS if membership.has(name)
            ]
        return data


# --------------------------------------------------------------------------
# Profil
# --------------------------------------------------------------------------
class ProfileSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=40)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=200)
    photo = serializers.ImageField(required=False, allow_null=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    role = serializers.SerializerMethodField()
    shop_name = serializers.CharField(read_only=True, default="")
    shop_currency = serializers.CharField(read_only=True, default="")
    is_owner = serializers.BooleanField(read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), read_only=True)
    avatar = serializers.SerializerMethodField()

    def get_role(self, obj) -> str:
        membership = get_membership(obj)
        if membership is None:
            return ""
        return "Propriétaire" if membership.is_owner else "Employé"

    def get_avatar(self, obj) -> dict:
        return avatar_data(obj)

    def validate_photo(self, value):
        # Mêmes règles que core.forms.ProfileForm : 2 Mo, JPEG/PNG/WebP/GIF.
        return clean_image_upload(
            value,
            max_bytes=2 * 1024 * 1024,
            max_label="2 Mo",
            allowed_types={"image/jpeg", "image/png", "image/webp", "image/gif"},
            formats_label="JPEG, PNG, WebP ou GIF",
            field_label="Photo",
        )

    def save_profile(self, user):
        profile = ensure_profile(user)
        data = self.validated_data
        photo = data.get("photo", None)
        if "photo" in data:
            profile.photo = photo
        if "phone" in data:
            profile.phone = data["phone"]
        if "bio" in data:
            profile.bio = data["bio"]
        profile.save()
        return profile


# --------------------------------------------------------------------------
# Suggestions (recherche de la barre supérieure)
# --------------------------------------------------------------------------
class SuggestionSerializer(serializers.Serializer):
    label = serializers.CharField()
    sub = serializers.CharField(allow_blank=True, default="")
    value = serializers.CharField()