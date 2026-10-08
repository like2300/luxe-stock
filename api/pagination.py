"""Pagination calquée sur le pied de page du web.

Le web affiche « Affichage de X à Y sur Z résultats » avec les boutons
Précédent / Suivant : la réponse renvoie ces compteurs déjà calculés, pour que
l'application n'ait pas à refaire l'arithmétique.

Produits : 10 par défaut, 10/25/50/100 proposés.
Mouvements : 15 par page (choix du web).
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class WebPagination(PageNumberPagination):
    page_size_query_param = "per"
    page_query_param = "page"
    max_page_size = 100

    default_per = 10
    allowed_per = (10, 25, 50, 100)

    def get_page_size(self, request):
        raw = request.query_params.get(self.page_size_query_param)
        try:
            per = int(raw)
        except (TypeError, ValueError):
            per = self.default_per
        # Un `per` hors liste retombe sur la valeur par defaut, comme sur le web
        # ou seule une valeur de la liste declenche le rendu du selecteur.
        return per if per in self.allowed_per else self.default_per

    def get_paginated_response(self, data):
        page = self.page
        count = page.paginator.count
        return Response(
            {
                "count": count,
                "page": page.number,
                "num_pages": page.paginator.num_pages,
                # 0 quand la liste est vide : « Affichage de 0 à 0 sur 0 résultats ».
                "start_index": (page.start_index() - 1) if count else 0,
                "end_index": page.end_index() if count else 0,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
                "results": data,
            }
        )


class MovementPagination(WebPagination):
    default_per = 15
    allowed_per = (10, 15, 25, 50, 100)


class NotificationPagination(WebPagination):
    """L'API renvoie le fil brut : le filtrage et la pagination 25 restent côté client.

    Le web fait de même (NOTIFICATION_FEED_LIMIT = 200 renvoyés d'un bloc, filtres
    et pagination ensuite en JavaScript).
    """

    default_per = 25
    allowed_per = (25,)