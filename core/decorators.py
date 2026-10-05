from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Membership


def shop_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        m = Membership.objects.select_related("shop").filter(user=request.user).first()
        if not m:
            return redirect("create_shop")
        request.membership, request.shop = m, m.shop
        return view(request, *args, **kwargs)
    return login_required(wrapper)


def perm_required(perm):
    def deco(view):
        @shop_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.membership.has(perm):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return deco


def owner_required(view):
    @shop_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.membership.is_owner:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def scanner_required(view):
    """Refuse l'acces quand le scanner est desactive pour la boutique.

    A poser sous un decorateur qui appelle shop_required : request.shop doit
    deja etre defini au moment du controle.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.shop.scanner_enabled:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper
