"""Outils partages par les tests de l'API.

Les tests d'API reutilisent les memes regles que le web : un proprietaire,
un employe avec un jeu de permissions donne, deux boutiques pour verifier
l'isolation.
"""

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from core.models import Category, Membership, Product, Shop

PASSWORD = "motdepasse-tres-long-1"


def make_user(username="alice", email=None, password=PASSWORD):
    """Compte connectable.

    `ACCOUNT_EMAIL_VERIFICATION = "none"` comme sur le web : aucun compte n'a
    besoin d'une adresse verifiee pour utiliser l'API.
    """
    from allauth.account.models import EmailAddress

    user = User.objects.create_user(
        username=username, email=email or f"{username}@exemple.test", password=password
    )
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
    return user


def make_owner_shop(username="patron", shop_name="Ma Boutique", **shop_kwargs):
    owner = make_user(username)
    shop = Shop.objects.create(owner=owner, name=shop_name, **shop_kwargs)
    Membership.objects.create(user=owner, shop=shop, is_owner=True)
    return owner, shop


def make_employee(shop, username="bob", **perms):
    """Employe avec le jeu de permissions demande ; tout le reste est refuse."""
    user = make_user(username)
    defaults = {
        "can_view_products": True,
        "can_add_products": False,
        "can_edit_products": False,
        "can_delete_products": False,
        "can_manage_stock": False,
        "can_manage_categories": False,
    }
    defaults.update(perms)
    membership = Membership.objects.create(user=user, shop=shop, **defaults)
    return user, membership


def api_client_for(user):
    """Client DRF authentifie par JWT, comme le fera l'application mobile."""
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
    return client


def anon_client():
    return APIClient()


def make_product(shop, name="Produit", quantity=0, category=None, **kwargs):
    return Product.objects.create(
        shop=shop, name=name, quantity=quantity, category=category, **kwargs
    )


def make_category(shop, name="Categorie"):
    return Category.objects.create(shop=shop, name=name)