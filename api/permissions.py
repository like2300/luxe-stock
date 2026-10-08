"""Règles d'accès de l'API.

Elles reprennent une à une celles du web (`core/decorators.py`) pour qu'aucune
écran ne soit accessible à un compte qui ne l'était pas :

- `shop_required`  -> `IsShopMember`   (409 `shop_required` au lieu d'une redirection)
- `perm_required`  -> `HasPermission`  (403)
- `owner_required` -> `IsShopOwner`    (403)
- `scanner_required` -> `ScannerEnabled` (403)

La vérification passe toujours par `Membership.has()`, qui accorde tout au
propriétaire : les drapeaux bruts ne sont jamais lus directement.
"""

from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from core.models import Membership

from .exceptions import ShopRequired


def get_membership(user):
    """Adhésion de l'utilisateur à une boutique, ou None."""
    if not user or not user.is_authenticated:
        return None
    return (
        Membership.objects.filter(user=user)
        .select_related("shop")
        .first()
    )


def _membership_or_401(request, view):
    """Adhésion de la requête, en distinguant « pas connecté » de « pas de boutique ».

    Sans cela, un visiteur anonyme recevrait 409 « créez une boutique », ce qui
    l'enverrait creer un compte dans le vide. Un 401 est la seule reponse utile.
    """
    if not request.user or not request.user.is_authenticated:
        raise exceptions.NotAuthenticated()
    membership = getattr(view, "membership", None) or get_membership(request.user)
    if membership is None:
        raise ShopRequired()
    return membership


class ShopScopedMixin:
    """Fournit `self.shop` et `self.membership` aux vues.

    Le décorateur `@login_required` du web devient la permission DRF par défaut
    (IsAuthenticated) ; ce mixin prend le relais pour l'appartenance à la
    boutique, qui est un état métier et non un simple droit.
    """

    def initial(self, request, *args, **kwargs):
        # Avant `super().initial()` : c'est lui qui evalue les permissions, qui
        # reutilisent alors cette adhésion au lieu de refaire la requete.
        self.membership = get_membership(request.user)
        self.shop = self.membership.shop if self.membership else None
        super().initial(request, *args, **kwargs)


class IsShopMember(BasePermission):
    """Utilisateur authentifié rattaché à une boutique."""

    def has_permission(self, request, view):
        membership = _membership_or_401(request, view)
        if membership is None:
            raise ShopRequired()
        return True


class IsShopOwner(BasePermission):
    """Propriétaire de la boutique (`owner_required`)."""

    message = "Accès interdit."

    def has_permission(self, request, view):
        membership = _membership_or_401(request, view)
        if membership is None:
            raise ShopRequired()
        if not membership.is_owner:
            return False
        return True


class HasPermission(BasePermission):
    """Permission nommée de `core.models.PERMISSIONS`.

    La permission est déclarée sur la vue, pas sur l'instance de permission :
    c'est donc `view.required_permission` qu'il faut lire.

    Exemple :
        class ProductCreate(ShopScopedMixin, HasPermission):
            required_permission = "can_add_products"
    """

    required_permission = None
    message = "Accès interdit."

    def has_permission(self, request, view):
        membership = _membership_or_401(request, view)
        if membership is None:
            raise ShopRequired()
        name = getattr(view, "required_permission", None) or self.required_permission
        if name and not membership.has(name):
            return False
        return True


class IsScannerEnabled(BasePermission):
    """Le scanner est facultatif : la boutique peut le masquer partout."""

    message = "Le scanner est désactivé pour cette boutique."

    def has_permission(self, request, view):
        shop = getattr(view, "shop", None) or _membership_or_401(request, view).shop
        return shop.scanner_enabled


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ("GET", "HEAD", "OPTIONS")