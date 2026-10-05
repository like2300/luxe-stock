from django import template
from django.utils.safestring import mark_safe

from core.avatar import avatar_gradient, avatar_data, user_initials, user_photo_url
from core.models import LEVEL_COLORS, NOTIFICATION_KINDS

register = template.Library()

LEVEL_LABELS = {"rupture": "Rupture", "bas": "Stock bas", "ok": "Stock sain"}


@register.filter
def level_label(value):
    """Traduit le code de niveau en libellé français."""
    return LEVEL_LABELS.get(value, value)


@register.simple_tag
def sound_codes():
    """Légende des codes son affichée sous le tableau des notifications."""
    return [{"code": code, "label": label, "tone": tone}
            for label, code, tone in NOTIFICATION_KINDS.values()]


@register.simple_tag
def level_palette():
    """Boutons de filtre par couleur : (code, libellé, fond, texte)."""
    return [{"code": code, "label": LEVEL_LABELS[code], "bg": bg, "fg": fg}
            for code, (bg, fg) in LEVEL_COLORS.items()]


# Les tags avatar lisent les memes donnees que le context processor "avatar" :
# ils servent aux gabarits qui n'utilisent pas base.html.
@register.simple_tag
def avatar(user):
    """Affiche la photo du profil, ou les initiales si aucune photo n'existe."""
    data = avatar_data(user)
    if data["has_photo"]:
        return mark_safe(
            '<img src="{}" alt="Photo de profil" class="w-full h-full object-cover">'.format(
                data["url"]
            )
        )
    return mark_safe(
        '<span class="w-full h-full flex items-center justify-center text-white font-semibold '
        'text-sm">{}</span>'.format(data["initials"])
    )


@register.simple_tag
def avatar_url(user):
    """URL de la photo du profil, ou chaine vide (les initiales sont affichees)."""
    return user_photo_url(user) or ""


@register.simple_tag
def avatar_initials(user):
    """Initiales de l'utilisateur (2 lettres maximum)."""
    return user_initials(user)


@register.simple_tag
def avatar_classes(user):
    """Classes Tailwind du degrade utilise quand aucune photo n'est disponible."""
    return avatar_gradient(user)