"""Service d'avatars : resolution de la photo et calcul des initiales.

La photo peut venir de deux sources, dans cet ordre :
1. la photo televersee par l'utilisateur (core.models.Profile.photo) ;
2. la photo fournie par le fournisseur OAuth (allauth, via le SocialAccount).

Si aucune source ne fournit d'image, l'interface affiche les initiales.
"""
from allauth.socialaccount.models import SocialAccount

# Couleurs stables : le degrade est choisi a partir du nom d'utilisateur
# afin que deux utilisateurs du meme nom n'aient pas le meme rendu.
GRADIENTS = [
    "from-primary to-indigo-400",
    "from-rose-500 to-orange-400",
    "from-emerald-500 to-teal-400",
    "from-sky-500 to-indigo-400",
    "from-amber-500 to-rose-400",
    "from-violet-500 to-fuchsia-400",
]


def get_profile(user):
    """Profil existant de l'utilisateur, ou None (aucune ecriture en base)."""
    from .models import Profile

    if not user or not user.is_authenticated:
        return None
    return Profile.objects.filter(user=user).first()


def ensure_profile(user):
    """Profil de l'utilisateur, cree a la volee s'il n'existe pas encore."""
    from .models import Profile

    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def user_initials(user):
    """Initiales de l'utilisateur : prenom + nom, sinon le pseudo (2 lettres max)."""
    if not user:
        return "?"

    parts = [p for p in (user.first_name.strip(), user.last_name.strip()) if p]
    if parts:
        initials = "".join(p[0] for p in parts)
    else:
        name = (user.get_full_name() or user.get_username() or "?").strip()
        pieces = name.split()
        initials = "".join(p[0] for p in pieces[:2]) or "?"

    return initials[:2].upper()


def social_photo_url(user):
    """Photo renvoyee par le fournisseur OAuth (Google), sinon None."""
    if not user or not user.is_authenticated:
        return None
# Depuis allauth 65, la photo du fournisseur est dans extra_data["picture"] ;
    # l'ancien champ SocialAccount.picture et l'API get_avatar_url n'existent plus.
    for account in SocialAccount.objects.filter(user=user):
        picture = (account.extra_data or {}).get("picture")
        if picture:
            return picture
    return None


def user_photo_url(user):
    """URL de la photo a afficher, ou None si l'utilisateur n'en a pas."""
    profile = get_profile(user)
    if profile and profile.photo:
        return profile.photo.url
    return social_photo_url(user)


def avatar_gradient(user):
    """Classes Tailwind du degrade de l'avatar, determinées par le nom d'utilisateur."""
    key = (user.get_username() if user and user.is_authenticated else "") or "?"
    return GRADIENTS[sum(ord(c) for c in key) % len(GRADIENTS)]


def avatar_data(user):
    """Donnees d'affichage de l'avatar : photo ou initiales + couleur."""
    photo = user_photo_url(user)
    return {
        "url": photo,
        "initials": user_initials(user),
        "gradient": avatar_gradient(user),
        "has_photo": bool(photo),
    }