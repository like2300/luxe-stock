"""Réponses d'erreur uniformes pour toute l'API.

Deux garanties :
- une erreur d'authentification ne renvoie jamais 403 (le web réserve le 403 à
  l'interdiction d'accès) ;
- un refus de validation garde la forme `{champ: message}` des formulaires web,
  pour que le client affiche les mêmes textes.
"""

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ShopRequired(exceptions.APIException):
    """Aucun compte n'est encore rattaché à une boutique."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Vous devez créer une boutique avant de continuer."
    default_code = "shop_required"


class RejectedOperation(Exception):
    """Refus métier d'une opération de synchronisation.

    Porte un code stable (`reason_code`) que le client utilise pour proposer une
    action, et un message en français repris des formulaires web.
    """

    def __init__(self, reason_code, reason, suggestion=None, detail=None):
        self.reason_code = reason_code
        self.reason = reason
        self.suggestion = suggestion or {}
        self.detail = detail
        super().__init__(reason)


def _flatten_drf_validation_error(data):
    """Transforme les erreurs DRF en `{champ: message}`.

    DRF renvoie `{champ: [msg, ...]}` ; le client affiche une seule ligne sous
    le champ, donc on garde le premier message.
    """
    errors = {}
    for field, value in (data or {}).items():
        if isinstance(value, (list, tuple)):
            errors[field] = str(value[0]) if value else ""
        elif isinstance(value, dict):
            errors.update(_flatten_drf_validation_error(value))
        else:
            errors[field] = str(value)
    return errors


def api_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        return Response(
            {"errors": _flatten_validation_error(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, DjangoPermissionDenied):
        return Response(
            {"detail": "Accès interdit.", "code": "permission_denied"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, Http404):
        return Response(
            {"detail": "Ressource introuvable.", "code": "not_found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, IntegrityError):
        # Les contraintes d'unicité partielles du core se déclenchent ici quand
        # deux requêtes concurrentes passent la validation du formulaire.
        message = "Cette donnée existe déjà."
        text = str(exc)
        for column in ("sku", "barcode", "name"):
            if column in text:
                message = {
                    "sku": "Cette référence existe déjà.",
                    "barcode": "Ce code-barres est déjà attribué à un autre produit de cette boutique.",
                    "name": "Cette catégorie existe déjà.",
                }[column]
                break
        return Response(
            {"detail": message, "code": "duplicate"},
            status=status.HTTP_409_CONFLICT,
        )

    response = drf_exception_handler(exc, context)

    if response is None:
        return None

    if isinstance(response.data, dict) and "detail" in response.data:
        return response

    response.data = {"errors": _flatten_drf_validation_error(response.data)}
    return response


def _flatten_validation_error(exc):
    if hasattr(exc, "message_dict"):
        return {field: msgs[0] if msgs else "" for field, msgs in exc.message_dict.items()}
    return {"non_field_errors": exc.messages[0] if exc.messages else ""}