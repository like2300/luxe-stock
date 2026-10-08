"""Points d'entrée de l'API REST.

Chaque vue reprend une vue du web (`core/views.py`) et renvoie du JSON. La
logique métier n'est jamais réimplémentée : `record_movement()`,
`record_adjustment()`, `push_notification()`, `notify_threshold_crossing()` et
`stock_history()` sont les originals du module `core`.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.avatar import ensure_profile
from core.models import (
    PERMISSIONS,
    Category,
    Membership,
    Product,
    Shop,
    StockMovement,
)
from core.views import NOTIFICATION_FEED_LIMIT, stock_history

from . import schema
from . import serializers as s
from .pagination import MovementPagination, WebPagination
from .payloads import profile_payload
from .permissions import (
    HasPermission,
    IsScannerEnabled,
    IsShopMember,
    IsShopOwner,
    ShopScopedMixin,
)
from .sync import SyncOperationsView, SyncPullView, SyncPushView, SyncStatusView  # noqa: F401


def shop_membership(user):
    """Adhesion de l'utilisateur, ou None.

    Renvoie None pour un visiteur non authentifie : filtrer `Membership` avec un
    `AnonymousUser` leve une TypeError et transformerait un 401 attendu en 500.
    """
    if not user or not user.is_authenticated:
        return None
    return Membership.objects.filter(user=user).select_related("shop").first()


def _bool_param(request, name):
    value = request.query_params.get(name, "")
    return value in ("1", "true", "True", "yes")


# --------------------------------------------------------------------------
# Authentification
# --------------------------------------------------------------------------
class LoginView(APIView):
    """Connexion : renvoie les jetons et le profil.

    Un compte sans boutique est connecte avec succes : l'application affiche
    alors l'ecran de creation de boutique (le web redirige vers la meme etape).
    """

    permission_classes = [AllowAny]
    throttle_scope = "login"
    serializer_class = s.LoginSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Se connecter",
        request=s.LoginSerializer,
        responses={200: schema.TokensSchema, 400: schema.ErrorSchema, 401: schema.ErrorSchema},
    )
    def post(self, request):
        serializer = s.LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": profile_payload(user, shop_membership(user)),
            }
        )


class SignupView(APIView):
    """Inscription : memes champs et memes messages que `SignupForm`."""

    permission_classes = [AllowAny]
    throttle_scope = "login"
    serializer_class = s.SignupSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Créer un compte",
        description="Mêmes champs et mêmes messages que le formulaire d'inscription du web.",
        request=s.SignupSerializer,
        responses={201: schema.TokensSchema, 400: schema.ErrorSchema},
    )
    def post(self, request):
        serializer = s.SignupSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": profile_payload(user, None),
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """Deconnexion : le jeton de rafraichissement est mis en liste noire."""

    permission_classes = [IsAuthenticated]
    serializer_class = s.LogoutSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Se déconnecter",
        request=s.LogoutSerializer,
        responses={200: schema.DetailSchema, 400: schema.ErrorSchema},
    )
    def post(self, request):
        serializer = s.LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw = serializer.validated_data["refresh"]
        try:
            RefreshToken(raw).blacklist()
        except TokenError:
            # Un jeton deja expire ou deja revoque : la deconnexion reste un
            # succes cote client, il n'y a plus rien a invalider.
            pass
        return Response({"detail": "Déconnexion effectuée."})


# --------------------------------------------------------------------------
# Boutique
# --------------------------------------------------------------------------
class ShopCreateView(ShopScopedMixin, APIView):
    """Creation de la boutique (apres inscription)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = s.ShopCreateSerializer

    @extend_schema(
        tags=["Boutique"],
        summary="Créer sa boutique",
        request=s.ShopCreateSerializer,
        responses={201: schema.ShopEnvelopeSchema, 409: schema.ErrorSchema},
    )
    def post(self, request):
        # Un compte deja rattache ne cree pas une seconde boutique : le web
        # redirige vers le tableau de bord.
        if shop_membership(request.user) is not None:
            return Response(
                {"detail": "Ce compte est déjà rattaché à une boutique.",
                 "code": "already_member"},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = s.ShopCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            shop = serializer.save(owner=request.user)
            Membership.objects.create(user=request.user, shop=shop, is_owner=True)
        return Response(
            {
                "shop": s.ShopSerializer(shop, context={"request": request}).data,
                "detail": "Votre boutique est prête. Ajoutez vos premiers produits !",
            },
            status=status.HTTP_201_CREATED,
        )


class ShopCurrentView(ShopScopedMixin, APIView):
    """Boutique courante : lecture et enregistrement des parametres."""

    permission_classes = [IsShopMember]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = s.ShopSerializer

    @extend_schema(tags=["Boutique"], summary="Lire la boutique courante",
                   responses={200: s.ShopSerializer})
    def get(self, request):
        return Response(s.ShopSerializer(self.shop, context={"request": request}).data)

    @extend_schema(
        tags=["Boutique"],
        summary="Enregistrer les paramètres",
        request=s.ShopSettingsSerializer,
        responses={200: schema.ShopEnvelopeSchema, 400: schema.ErrorSchema, 403: schema.ErrorSchema},
    )
    def put(self, request):
        if not self.membership.is_owner:
            return Response(
                {"detail": "Accès interdit.", "code": "permission_denied"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = s.ShopSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save_shop(self.shop)
        return Response(
            {
                "shop": s.ShopSerializer(self.shop, context={"request": request}).data,
                "detail": "Paramètres enregistrés.",
            }
        )

    def reset_theme(self, request):
        """Remet les quatre couleurs aux valeurs par defaut du modele."""
        return _reset_theme(self.membership, self.shop, request)


def _reset_theme(membership, shop, request):
    if not membership.is_owner:
        return Response(
            {"detail": "Accès interdit.", "code": "permission_denied"},
            status=status.HTTP_403_FORBIDDEN,
        )
    for field in ("primary_color", "sidebar_color", "header_color", "background_color"):
        setattr(shop, field, Shop._meta.get_field(field).default)
    shop.save()
    return Response(
        {
            "shop": s.ShopSerializer(shop, context={"request": request}).data,
            "detail": "Thème réinitialisé.",
        }
    )


class ShopThemeResetView(ShopScopedMixin, IsShopOwner, APIView):
    """Remet les quatre couleurs aux valeurs par defaut du modele (« Thème
    réinitialisé. »)."""

    permission_classes = [IsShopOwner]

    @extend_schema(tags=["Boutique"], summary="Réinitialiser le thème",
                   request=None, responses={200: schema.ShopEnvelopeSchema})
    def post(self, request):
        return _reset_theme(self.membership, self.shop, request)


# --------------------------------------------------------------------------
# Tableau de bord
# --------------------------------------------------------------------------
class DashboardView(ShopScopedMixin, HasPermission, APIView):
    """Indicateurs, produits a reapprovisionner, derniers mouvements, graphique."""

    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(
        tags=["Boutique"],
        summary="Tableau de bord",
        description="Indicateurs, 8 premiers produits à réapprovisionner, "
                    "8 derniers mouvements et série sur 6 mois.",
        responses={200: schema.DashboardSchema},
    )
    def get(self, request):
        shop = self.shop
        products = shop.products.all()
        # Revenu total : Somme(quantite x prix d'achat), comme sur le web.
        value = (
            products.aggregate(
                v=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("cost_price"),
                        output_field=DecimalField(max_digits=18, decimal_places=2),
                    )
                )
            )["v"]
            or 0
        )
        low_qs = products.filter(quantity__lte=F("alert_threshold"))
        name = request.user.get_full_name() or request.user.get_username()
        return Response(
            {
                "greeting_name": name,
                "currency": shop.currency,
                "n_products": products.count(),
                "n_categories": shop.categories.count(),
                "n_low": low_qs.count(),
                "value": str(value),
                # Le badge « +N% » du web n'est branche a aucune donnee : on le
                # renvoie a zero plutot que d'inventer un calcul.
                "value_increase": 0,
                "low_products": s.ProductListSerializer(
                    low_qs.order_by("quantity")[:8], many=True
                ).data,
                "recent_movements": s.MovementSerializer(
                    StockMovement.objects.filter(product__shop=shop).select_related(
                        "product", "user"
                    )[:8],
                    many=True,
                ).data,
                # Serie sur 6 mois reutilisee telle quelle depuis le web.
                "chart": stock_history(shop),
            }
        )


# --------------------------------------------------------------------------
# Produits
# --------------------------------------------------------------------------
class ProductViewSet(viewsets.ModelViewSet):
    """Produits : liste filtree, creation, modification, suppression logique."""

    serializer_class = s.ProductSerializer
    pagination_class = WebPagination
    lookup_field = "uuid"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsShopMember(), HasPermission()]
        if self.action == "create":
            return [IsShopMember(), _Named("can_add_products")]
        if self.action in ("update", "partial_update"):
            return [IsShopMember(), _Named("can_edit_products")]
        if self.action == "destroy":
            return [IsShopMember(), _Named("can_delete_products")]
        return super().get_permissions()

    # -- boutique et permissions ------------------------------------------
    def initial(self, request, *args, **kwargs):
        # Resolu avant l'evaluation des permissions : `IsShopMember` et
        # `HasPermission` reutilisent cette requete au lieu d'en faire une seconde.
        self._membership = shop_membership(request.user)
        self._shop = self._membership.shop if self._membership else None
        super().initial(request, *args, **kwargs)

    @property
    def membership(self):
        return self._membership

    @property
    def shop(self):
        # `getattr` : drf-spectacular instancie la vue sans passer par `initial()`.
        return getattr(self, "_shop", None)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"shop": self._shop, "membership": self._membership})
        return context

    def get_queryset(self):
        shop = self.shop
        if shop is None:
            return Product.objects.none()
        return shop.products.select_related("category")

    def get_serializer_class(self):
        if self.action in ("list",):
            return s.ProductListSerializer
        return s.ProductSerializer

    # -- filtres (identiques a la liste du web) -------------------------
    def filter_queryset(self, queryset):
        params = self.request.query_params
        q = params.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(sku__icontains=q) | Q(category__name__icontains=q)
            )
        category = params.get("category", "").strip()
        if category:
            queryset = _filter_by_category(queryset, self._shop, category)
        if _bool_param(self.request, "low"):
            queryset = queryset.filter(quantity__lte=F("alert_threshold"))
        # Meme semantique que la propriete `Product.level`, traduite en requete :
        # `rupture` = 0, `bas` = entre 1 et le seuil, `ok` = au-dessus.
        level = params.get("level", "").strip()
        if level == "rupture":
            queryset = queryset.filter(quantity__lte=0)
        elif level == "bas":
            queryset = queryset.filter(quantity__gt=0, quantity__lte=F("alert_threshold"))
        elif level == "ok":
            queryset = queryset.filter(quantity__gt=F("alert_threshold"))
        return queryset

    def perform_create(self, serializer):
        shop = self._shop
        # Champ « Code-barres » masque : le code lu par le scanner est quand
        # meme enregistre, sauf s'il est deja attribue (cf. product_create).
        if not shop.barcode_field_enabled:
            scanned = self.request.query_params.get("barcode", "").strip()[:64]
            if scanned:
                normalized = "".join(scanned.split())
                if not shop.products.filter(barcode=normalized).exists():
                    serializer.validated_data["barcode"] = normalized
        serializer.save()

    def perform_destroy(self, instance):
        # Suppression logique : la ligne doit rester visible du pull pour que
        # les autres appareils l'apprennent.
        instance.soft_delete()

    @action(detail=False, methods=["post"])
    @extend_schema(
        tags=["Produits"],
        summary="Supprimer plusieurs produits",
        description="Suppression logique : « N produit(s) supprimé(s). »",
        request=inline_serializer(
            name="SuppressionMultiple",
            fields={"uuids": serializers.ListField(child=serializers.UUIDField())},
        ),
        responses={200: schema.DetailSchema, 400: schema.ErrorSchema},
    )
    def bulk_delete(self, request):
        """Suppression multiple (« N produit(s) supprimé(s). »)."""
        ids = (request.data or {}).get("uuids") or []
        if not isinstance(ids, list) or not ids:
            return Response(
                {"detail": "Aucun produit sélectionné."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        products = self.get_queryset().filter(uuid__in=ids)
        count = products.count()
        for product in products:
            product.soft_delete()
        return Response({"count": count, "detail": f"{count} produit(s) supprimé(s)."})

    @extend_schema(tags=["Produits"], summary="Supprimer un produit",
                   request=None, responses={200: schema.DetailSchema, 404: schema.ErrorSchema})
    def destroy(self, request, *args, **kwargs):
        """200 et non 204 : le message francais du web est affiche par l'app."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Produit supprimé."})


class _Named(HasPermission):
    """Permission nommee choisie au moment de la verification."""

    def __init__(self, permission):
        super().__init__()
        self.required_permission = permission


def _filter_by_category(queryset, shop, value):
    """Filtre par catégorie : identifiant, uuid ou nom — comme le web."""
    try:
        import uuid as uuid_lib

        return queryset.filter(category__uuid=uuid_lib.UUID(value))
    except (ValueError, AttributeError, TypeError):
        pass
    if value.isdigit():
        return queryset.filter(category_id=value)
    return queryset.filter(category__name__iexact=value)


# --------------------------------------------------------------------------
# Catégories
# --------------------------------------------------------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    """Catégories : liste avec compteur de produits, creation, suppression."""

    lookup_field = "uuid"
    http_method_names = ["get", "post", "put", "delete", "head", "options"]
    serializer_class = s.CategorySerializer
    queryset = Category.objects.all()

    def initial(self, request, *args, **kwargs):
        self._membership = shop_membership(request.user)
        self._shop = self._membership.shop if self._membership else None
        super().initial(request, *args, **kwargs)

    @property
    def membership(self):
        return self._membership

    @property
    def shop(self):
        return getattr(self, "_shop", None)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsShopMember(), _Named("can_view_products")]
        return [IsShopMember(), _Named("can_manage_categories")]

    def get_queryset(self):
        return (
            Category.objects.filter(shop=self._shop)
            # Le compteur ignore les produits supprimes logiquement.
            .annotate(
                product_count=Count(
                    "products", filter=Q(products__deleted_at__isnull=True)
                )
            )
            .order_by("name")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["shop"] = self._shop
        return context

    def perform_destroy(self, instance):
        # Le web met les produits sans categorie (on_delete=SET_NULL). La
        # suppression logique doit avoir le meme effet visible.
        now = timezone.now()
        Product.objects.filter(category=instance).update(category=None, updated_at=now)
        instance.deleted_at = now
        instance.save(update_fields=["deleted_at", "updated_at"])


# --------------------------------------------------------------------------
# Mouvements
# --------------------------------------------------------------------------
class MovementViewSet(viewsets.ModelViewSet):
    """Mouvements : liste filtree et enregistrement via `record_movement()`."""

    serializer_class = s.MovementSerializer
    pagination_class = MovementPagination
    http_method_names = ["get", "post", "head", "options"]
    # Attribut present pour l'introspection OpenAPI ; le filtrage reelle se fait
    # dans `get_queryset()`.
    queryset = StockMovement.objects.all()

    def initial(self, request, *args, **kwargs):
        self._membership = shop_membership(request.user)
        self._shop = self._membership.shop if self._membership else None
        super().initial(request, *args, **kwargs)

    @property
    def membership(self):
        return self._membership

    @property
    def shop(self):
        return getattr(self, "_shop", None)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsShopMember(), _Named("can_view_products")]
        return [IsShopMember(), _Named("can_manage_stock")]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["shop"] = self._shop
        return context

    def get_queryset(self):
        return StockMovement.objects.filter(product__shop=self._shop).select_related(
            "product", "user"
        )

    def filter_queryset(self, queryset):
        params = self.request.query_params
        q = params.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(product__name__icontains=q)
                | Q(product__sku__icontains=q)
                | Q(note__icontains=q)
                | Q(user__username__icontains=q)
            )
        kind = params.get("type", "")
        if kind in (StockMovement.IN, StockMovement.OUT):
            queryset = queryset.filter(kind=kind)
        product_ref = params.get("product", "").strip()
        if product_ref:
            try:
                import uuid as uuid_lib

                queryset = queryset.filter(product__uuid=uuid_lib.UUID(product_ref))
            except (ValueError, AttributeError, TypeError):
                if product_ref.isdigit():
                    queryset = queryset.filter(product_id=product_ref)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movement = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------
# Notifications
# --------------------------------------------------------------------------
class NotificationListView(ShopScopedMixin, HasPermission, APIView):
    """Fil des notifications.

    Le web renvoie un lot de 200 et fait le filtrage et la pagination 25 dans le
    navigateur. L'API renvoie le meme lot ; les filtres sont acceptes en plus,
    ce qui evite au client de telecharger 200 lignes pour une recherche.
    """

    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(
        tags=["Notifications"],
        summary="Fil des notifications",
        description="Lot de 200 notifications, comme le web. Les filtres (q, level, "
                    "unread) sont optionnels.",
        parameters=[
            OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("level", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             enum=["rupture", "bas", "ok"]),
            OpenApiParameter("unread", OpenApiTypes.BOOL, OpenApiParameter.QUERY),
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses={200: schema.NotificationFeedSchema},
    )
    def get(self, request):
        qs = self.shop.notifications.select_related("product", "user")
        params = request.query_params

        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(message__icontains=q)
                | Q(product__name__icontains=q)
                | Q(label__icontains=q)
                | Q(sound_code__icontains=q)
            )
        level = params.get("level", "").strip()
        if level in ("rupture", "bas", "ok"):
            qs = qs.filter(level=level)
        if _bool_param(request, "unread"):
            qs = qs.filter(is_read=False)

        total = qs.count()
        try:
            limit = int(params.get("limit", NOTIFICATION_FEED_LIMIT))
        except (TypeError, ValueError):
            limit = NOTIFICATION_FEED_LIMIT
        limit = max(1, min(limit, NOTIFICATION_FEED_LIMIT))
        rows = list(qs[:limit])
        return Response(
            {
                "count": total,
                "truncated": max(total - len(rows), 0),
                "limit": limit,
                "unread_count": self.shop.notifications.filter(is_read=False).count(),
                "results": s.NotificationSerializer(rows, many=True).data,
            }
        )


class NotificationReadView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(tags=["Notifications"], summary="Marquer une notification comme lue",
                   request=None, responses={200: s.NotificationSerializer, 404: schema.ErrorSchema})
    def post(self, request, uuid):
        notification = _get_notification(self.shop, uuid)
        if notification is None:
            return Response(
                {"detail": "Notification introuvable.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return Response(s.NotificationSerializer(notification).data)


class NotificationReadAllView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(tags=["Notifications"], summary="Tout marquer comme lu",
                   request=None, responses={200: schema.NotificationReadAllSchema})
    def post(self, request):
        count = self.shop.notifications.filter(is_read=False).update(
            is_read=True, updated_at=timezone.now()
        )
        return Response(
            {"count": count, "detail": f"{count} notification(s) marquée(s) comme lue(s)."}
        )


class NotificationClearView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(tags=["Notifications"],
                   summary="Tout effacer (suppression logique)",
                   request=None, responses={200: schema.NotificationReadAllSchema})
    def delete(self, request):
        count = self.shop.notifications.count()
        for notification in self.shop.notifications.all():
            notification.soft_delete()
        return Response({"count": count, "detail": f"{count} notification(s) supprimée(s)."})


def _get_notification(shop, uuid):
    try:
        return shop.notifications.filter(uuid=uuid).first()
    except (ValueError, TypeError, ValidationError):
        return None


# --------------------------------------------------------------------------
# Employés
# --------------------------------------------------------------------------
class EmployeeListCreateView(ShopScopedMixin, IsShopOwner, APIView):
    """Comptes des employés : propriétaire uniquement (`owner_required`)."""

    permission_classes = [IsShopOwner]

    @extend_schema(
        tags=["Employés"],
        summary="Lister les employés",
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={200: schema.EmployeeListSchema},
    )
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        members = self.shop.members.filter(is_owner=False).select_related("user")
        if q:
            members = members.filter(
                Q(user__username__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__email__icontains=q)
            )
        serializer = s.EmployeeSerializer(
            [_user_with_membership(m) for m in members.order_by("user__username")],
            many=True,
        )
        return Response({"count": len(serializer.data), "results": serializer.data})

    @extend_schema(
        tags=["Employés"],
        summary="Créer un compte employé",
        request=s.EmployeeCreateSerializer,
        responses={201: s.EmployeeSerializer, 400: schema.ErrorSchema},
    )
    def post(self, request):
        serializer = s.EmployeeCreateSerializer(
            data=request.data, context={"request": request, "shop": self.shop}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"detail": f"Compte « {user.get_username()} » créé.", **serializer.data},
            status=status.HTTP_201_CREATED,
        )


class EmployeeDetailView(ShopScopedMixin, IsShopOwner, APIView):
    permission_classes = [IsShopOwner]

    def _membership_for(self, uuid):
        return self.shop.members.filter(is_owner=False, uuid=uuid).select_related("user").first()

    @extend_schema(tags=["Employés"], summary="Lire un employé", operation_id="employees_detail_get",
                   responses={200: s.EmployeeSerializer, 404: schema.ErrorSchema})
    def get(self, request, uuid):
        membership = self._membership_for(uuid)
        if membership is None:
            return Response(
                {"detail": "Employé introuvable.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(s.EmployeeSerializer(_user_with_membership(membership)).data)

    @extend_schema(
        tags=["Employés"],
        summary="Modifier un employé",
        description="Mot de passe facultatif : « Laisser vide pour ne pas changer. »",
        request=s.EmployeeSerializer,
        responses={200: s.EmployeeSerializer, 400: schema.ErrorSchema, 404: schema.ErrorSchema},
    )
    def put(self, request, uuid):
        membership = self._membership_for(uuid)
        if membership is None:
            return Response(
                {"detail": "Employé introuvable.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = _user_with_membership(membership)
        serializer = s.EmployeeSerializer(
            user, data=request.data, context={"request": request, "employee": user}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user.username = data.get("username", user.username)
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data.get("email", user.email)
        # « Laisser vide pour ne pas changer. »
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        for name, _label in PERMISSIONS:
            if name in data:
                setattr(membership, name, data[name])
        membership.save()
        # Relecture : `serializer.data` decrirait encore l'adherence d'avant
        # la sauvegarde, donc des permissions obsoletees.
        updated = _user_with_membership(membership)
        return Response(
            {"detail": "Employé mis à jour.", **s.EmployeeSerializer(updated, context={"request": request}).data}
        )

    @extend_schema(tags=["Employés"], summary="Supprimer un compte employé",
                   request=None, responses={200: schema.DetailSchema, 404: schema.ErrorSchema})
    def delete(self, request, uuid):
        membership = self._membership_for(uuid)
        if membership is None:
            return Response(
                {"detail": "Employé introuvable.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        membership.user.delete()
        return Response({"detail": "Compte employé supprimé."})


def _user_with_membership(membership):
    """User annotate de sa `membership`, pour `granted_permissions`."""
    user = membership.user
    user.membership = membership
    return user


# --------------------------------------------------------------------------
# Profil
# --------------------------------------------------------------------------
class ProfileView(ShopScopedMixin, IsShopMember, APIView):
    """Profil du compte connecte : photo, telephone, bio, role."""

    permission_classes = [IsShopMember]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = s.ProfileSerializer

    @extend_schema(tags=["Profil"], summary="Lire le profil",
                   responses={200: s.ProfileSerializer})
    def get(self, request):
        return Response(profile_payload(request.user, self.membership))

    @extend_schema(
        tags=["Profil"],
        summary="Modifier le profil",
        description="Photo (JPEG, PNG, WebP ou GIF, 2 Mo maximum), téléphone et bio.",
        request=s.ProfileSerializer,
        responses={200: s.ProfileSerializer, 400: schema.ErrorSchema},
    )
    def put(self, request):
        serializer = s.ProfileSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user
        # Le nom affichable peut aussi changer ici (champ en lecture seule sur
        # l'API mais editable sur le web) : on ne le touche pas, l'inscription
        # reste le seul endroit qui le fixe.
        serializer.save_profile(user)
        return Response(
            {"detail": "Profil mis à jour.", **profile_payload(user, self.membership)}
        )


class ProfilePhotoDeleteView(ShopScopedMixin, IsShopMember, APIView):
    """Retire la photo televersee : l'interface rebascule sur les initiales."""

    permission_classes = [IsShopMember]

    @extend_schema(tags=["Profil"], summary="Retirer la photo",
                   request=None, responses={200: s.ProfileSerializer})
    def delete(self, request):
        profile = ensure_profile(request.user)
        if profile.photo:
            profile.photo.delete(save=False)
            profile.save(update_fields=["photo", "updated_at"])
        return Response(
            {
                "detail": "Photo retirée — vos initiales sont affichées.",
                **profile_payload(request.user, self.membership),
            }
        )


# --------------------------------------------------------------------------
# Scanner
# --------------------------------------------------------------------------
def scan_payload(product):
    """Produit renvoye par le scan (meme forme que `_scan_payload` du web)."""
    return {
        "found": True,
        "uuid": str(product.uuid),
        "id": product.pk,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "category": product.category.name if product.category else "",
        "stock": product.quantity,
        "sale_price": str(product.sale_price),
        "level": product.level,
    }


class ScanConfigView(ShopScopedMixin, IsShopMember, HasPermission, IsScannerEnabled, APIView):
    """Reglages de l'ecran de scan : modes autorises et boutons visibles."""

    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission, IsScannerEnabled]

    @extend_schema(tags=["Produits"], summary="Réglages de l'écran de scan",
                   responses={200: schema.ScanConfigSchema, 403: schema.ErrorSchema})
    def get(self, request):
        can_manage = self.membership.has("can_manage_stock")
        return Response(
            {
                "scanner_enabled": self.shop.scanner_enabled,
                # Reglee separement : la boutique peut garder le scanner en
                # retirant le champ « Code-barres » des formulaires produit.
                "barcode_field_enabled": self.shop.barcode_field_enabled,
                "can_manage_stock": can_manage,
                "can_add_products": self.membership.has("can_add_products"),
                "can_edit_products": self.membership.has("can_edit_products"),
                # Sans droit de stock, le scan se limite a la fiche produit.
                "modes": ["OUT", "IN", "CARD"] if can_manage else ["CARD"],
                "default_mode": "OUT" if can_manage else "CARD",
            }
        )


class ScanLookupView(ShopScopedMixin, IsShopMember, HasPermission, IsScannerEnabled, APIView):
    """Retrouve un produit par code-barres, puis par reference."""

    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission, IsScannerEnabled]

    @extend_schema(
        tags=["Produits"],
        summary="Retrouver un produit scanné",
        description="Code-barres d'abord, puis référence. Limité à la boutique du membre.",
        parameters=[OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY,
                                     required=True)],
        responses={200: schema.ScanLookupSchema},
    )
    def get(self, request):
        code = "".join(request.query_params.get("code", "").split())[:64]
        if not code:
            return Response({"found": False, "message": "Aucun code reçu."})
        products = self.shop.products.select_related("category")
        product = products.filter(barcode=code).first() or products.filter(sku=code).first()
        if product is None:
            # Code inconnu : l'interface propose de creer le produit avec ce code.
            return Response({"found": False, "code": code})
        return Response(scan_payload(product))


class ScanMovementBatchView(ShopScopedMixin, IsShopMember, HasPermission, IsScannerEnabled, APIView):
    """Enregistre un lot de sorties ou d'entrees scanné, de façon atomique."""

    required_permission = "can_manage_stock"
    permission_classes = [IsShopMember, HasPermission, IsScannerEnabled]
    serializer_class = s.ScanBatchSerializer

    @extend_schema(
        tags=["Produits"],
        summary="Enregistrer un lot scanné",
        description="Atomique : si une ligne est refusée, rien n'est enregistré.",
        request=s.ScanBatchSerializer,
        responses={200: schema.ScanBatchResultSchema, 400: schema.ErrorSchema},
    )
    def post(self, request):
        # `APIView` n'a pas de `get_serializer()` : on instancie directement.
        serializer = s.ScanBatchSerializer(
            data=request.data, context={"request": request, "shop": self.shop}
        )
        serializer.is_valid(raise_exception=True)
        summary = serializer.save_batch()
        return Response({"ok": True, "kind": serializer.validated_data["kind"],
                         "count": len(summary), "items": summary})


# --------------------------------------------------------------------------
# Suggestions (barre de recherche superieure)
# --------------------------------------------------------------------------
def _suggest_q(request, max_len=60):
    return request.query_params.get("q", "").strip()[:max_len]


class SuggestProductsView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(
        tags=["Produits"],
        summary="Suggestions",
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={200: schema.SuggestionSchema},
    )
    def get(self, request):
        q = _suggest_q(request)
        qs = self.shop.products.select_related("category")
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(sku__icontains=q) | Q(category__name__icontains=q)
            )
        rows = qs.order_by("name")[:8]
        return Response(
            {
                "results": [
                    {
                        "label": p.name,
                        "sub": " — ".join(
                            x for x in [p.sku, p.category.name if p.category else ""] if x
                        ),
                        "value": p.name,
                    }
                    for p in rows
                ]
            }
        )


class SuggestCategoriesView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(
        tags=["Produits"],
        summary="Suggestions",
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={200: schema.SuggestionSchema},
    )
    def get(self, request):
        q = _suggest_q(request)
        qs = self.shop.categories.annotate(
            n_products=Count("products", filter=Q(products__deleted_at__isnull=True))
        )
        if q:
            qs = qs.filter(name__icontains=q)
        return Response(
            {
                "results": [
                    {
                        "label": c.name,
                        "sub": f"{c.n_products} produit{'s' if c.n_products != 1 else ''}",
                        "value": c.name,
                    }
                    for c in qs.order_by("name")[:8]
                ]
            }
        )


class SuggestMovementsView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(
        tags=["Produits"],
        summary="Suggestions",
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={200: schema.SuggestionSchema},
    )
    def get(self, request):
        q = _suggest_q(request)
        qs = StockMovement.objects.filter(product__shop=self.shop).select_related("product")
        if q:
            qs = qs.filter(
                Q(product__name__icontains=q)
                | Q(product__sku__icontains=q)
                | Q(note__icontains=q)
            )
        return Response(
            {
                "results": [
                    {
                        "label": m.product.name,
                        "sub": f"{m.get_kind_display()} — {m.quantity}",
                        "value": m.product.name,
                    }
                    for m in qs.order_by("-created_at", "-id")[:8]
                ]
            }
        )


class SuggestEmployeesView(ShopScopedMixin, IsShopOwner, APIView):
    permission_classes = [IsShopOwner]

    @extend_schema(
        tags=["Produits"],
        summary="Suggestions",
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={200: schema.SuggestionSchema},
    )
    def get(self, request):
        q = _suggest_q(request)
        qs = self.shop.members.filter(is_owner=False).select_related("user")
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
            )
        return Response(
            {
                "results": [
                    {
                        "label": m.user.get_full_name() or m.user.get_username(),
                        "sub": m.user.username,
                        "value": m.user.username,
                    }
                    for m in qs.order_by("user__username")[:8]
                ]
            }
        )


class SuggestNotificationsView(ShopScopedMixin, HasPermission, APIView):
    required_permission = "can_view_products"
    permission_classes = [IsShopMember, HasPermission]

    @extend_schema(
        tags=["Produits"],
        summary="Suggestions",
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={200: schema.SuggestionSchema},
    )
    def get(self, request):
        q = _suggest_q(request)
        qs = self.shop.notifications.select_related("product")
        if q:
            qs = qs.filter(
                Q(message__icontains=q)
                | Q(product__name__icontains=q)
                | Q(label__icontains=q)
            )
        return Response(
            {
                "results": [
                    {"label": n.message[:80], "sub": n.label, "value": n.message[:60]}
                    for n in qs.order_by("-created_at", "-id")[:8]
                ]
            }
        )