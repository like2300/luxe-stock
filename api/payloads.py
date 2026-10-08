"""Représentation JSON des entités, partagée par l'API REST et la synchronisation.

Le `pull` et les endpoints REST doivent renvoyer exactement la même forme pour
une même ligne : ces fonctions sont donc écrites une seule fois ici.
"""

from core.avatar import avatar_data, ensure_profile
from core.models import PERMISSIONS

from . import serializers as s


def shop_payload(shop):
    return s.ShopSerializer(shop).data


def category_payload(category):
    return s.CategorySerializer(category).data


def membership_payload(membership):
    """Adhésion : permissions accordées, résolues comme dans la liste des employés."""
    return {
        "uuid": str(membership.uuid),
        "username": membership.user.get_username(),
        "full_name": membership.user.get_full_name() or membership.user.get_username(),
        "is_owner": membership.is_owner,
        "role": "Propriétaire" if membership.is_owner else "Employé",
        "granted_permissions": [
            label for name, label in PERMISSIONS if membership.has(name)
        ],
        "permissions": {
            name: membership.has(name) for name, _label in PERMISSIONS
        },
        "updated_at": membership.updated_at,
    }


def profile_payload(user, membership):
    """Identité, rôle, boutique et avatar — même contenu que `_profile_payload`."""
    profile = ensure_profile(user)
    data = {
        "uuid": str(profile.uuid),
        "username": user.get_username(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.get_full_name() or user.get_username(),
        "email": user.email,
        "phone": profile.phone,
        "bio": profile.bio,
        "date_joined": user.date_joined,
        "last_login": user.last_login,
        "avatar": avatar_data(user),
    }
    if membership:
        data.update(
            {
                "shop_uuid": str(membership.shop.uuid),
                "shop_name": membership.shop.name,
                "shop_currency": membership.shop.currency,
                "is_owner": membership.is_owner,
                "role": "Propriétaire" if membership.is_owner else "Employé",
                # Libellés des permissions accordees, dans l'ordre de PERMISSIONS.
                "permissions": [label for name, label in PERMISSIONS if membership.has(name)],
            }
        )
    else:
        data.update(
            {
                "shop_uuid": None,
                "shop_name": "",
                "shop_currency": "",
                "is_owner": False,
                "role": "",
                "permissions": [],
            }
        )
    return data