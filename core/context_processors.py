from django.conf import settings
from django.db.models import F
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .avatar import avatar_data
from .models import PERMISSIONS, Membership

# Horodatage de la derniere notification montree en toast, memorize en session.
SEEN_AT_KEY = "notifications_seen_at"

# Nombre d'alertes montrees d'un coup : au-dela, la pile iOS deviendrait
# illisible et le creneau de session n'avancerait que sur la page suivante.
MAX_PENDING = 3


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


def pending_notifications(request, shop):
    """Alertes creees depuis la derniere page vue, destinees aux toasts.

    Le creneau est garde en session : sans lui, chaque rechargement repeterait
    les memes notifications. Il avance sur la plus recente des affichees, les
    suivantes restant en attente pour la page d'apres.
    """
    seen_at = parse_datetime(request.session.get(SEEN_AT_KEY) or "")
    if seen_at is None:
        # Premiere visite : le creneau se cale sur l'instant present, jamais sur
        # l'historique — on ne rattrape pas une boutique deja bruyante, et la
        # premiere alerte tombee ensuite sera bien poussee.
        seen_at = timezone.now()
        request.session[SEEN_AT_KEY] = seen_at.isoformat()
    pending = list(
        shop.notifications.filter(created_at__gt=seen_at).order_by("created_at")[:MAX_PENDING]
    )
    if pending:
        request.session[SEEN_AT_KEY] = pending[-1].created_at.isoformat()
    return pending


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
        "new_notifications": pending_notifications(request, m.shop),
    }
