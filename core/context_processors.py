from django.conf import settings
from django.db.models import F

from .avatar import avatar_data
from .models import PERMISSIONS, Membership


def social_login(request):
    """Le bouton Google n'est affiché que si le client OAuth est réellement configuré,
    sinon allauth renvoie une erreur « provider not configured » au clic."""
    provider = settings.SOCIALACCOUNT_PROVIDERS.get("google", {}).get("APP", {})
    return {"google_oauth_enabled": bool(provider.get("client_id") and provider.get("secret"))}


def avatar(request):
    """Avatar de l'utilisateur connecté, disponible dans tous les gabarits.

    Expose la photo (televersée ou fournie par Google) et, à défaut, les
    initiales : le gabarit affiche l'un ou l'autre sans filtre personnalisé.
    """
    u = getattr(request, "user", None)
    if not u or not u.is_authenticated:
        return {}
    data = avatar_data(u)
    return {
        "avatar": data,
        "avatar_photo": data["url"] or "",
        "avatar_initials": data["initials"],
        "avatar_gradient": data["gradient"],
    }


def shop(request):
    u = getattr(request, "user", None)
    if not u or not u.is_authenticated:
        return {}
    m = getattr(request, "membership", None) or Membership.objects.select_related("shop").filter(user=u).first()
    if not m:
        return {}
    return {
        "shop": m.shop,
        "membership": m,
        "sp": {name: m.has(name) for name, _ in PERMISSIONS},
        "low_count": m.shop.products.filter(quantity__lte=F("alert_threshold")).count(),
        "unread_count": m.shop.notifications.filter(is_read=False).count(),
    }
