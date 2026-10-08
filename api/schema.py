"""Schémas OpenAPI des réponses à enveloppe propre.

Les endpoints REST utilisent des sérialiseurs DRF, que drf-spectacular déduit
tout seul. Les endpoints à réponse sur mesure (tableau de bord, scan,
synchronisation) sont décrits ici : la documentation reste complète, ce qui est
le but de `drf-spectacular`.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

# ---------- Envelopes simples ----------
DetailSchema = inline_serializer(
    name="Detail",
    fields={"detail": serializers.CharField()},
)

ErrorSchema = inline_serializer(
    name="Erreur",
    fields={
        "detail": serializers.CharField(required=False),
        "code": serializers.CharField(required=False),
        "reason_code": serializers.CharField(required=False),
        "suggestion": serializers.DictField(required=False),
        "errors": serializers.DictField(required=False),
    },
)

TokensSchema = inline_serializer(
    name="Jeton",
    fields={
        "access": serializers.CharField(),
        "refresh": serializers.CharField(),
        "user": serializers.DictField(),
    },
)

# ---------- Boutique ----------
ShopEnvelopeSchema = inline_serializer(
    name="BoutiqueReponse",
    fields={
        "shop": serializers.DictField(),
        "detail": serializers.CharField(required=False),
    },
)

# ---------- Tableau de bord ----------
DashboardSchema = inline_serializer(
    name="TableauDeBord",
    fields={
        "greeting_name": serializers.CharField(),
        "currency": serializers.CharField(),
        "n_products": serializers.IntegerField(),
        "n_categories": serializers.IntegerField(),
        "n_low": serializers.IntegerField(),
        "value": serializers.CharField(),
        "value_increase": serializers.IntegerField(),
        "low_products": serializers.ListField(child=serializers.DictField()),
        "recent_movements": serializers.ListField(child=serializers.DictField()),
        "chart": serializers.DictField(),
    },
)

# ---------- Notifications ----------
NotificationFeedSchema = inline_serializer(
    name="FilNotifications",
    fields={
        "count": serializers.IntegerField(),
        "truncated": serializers.IntegerField(),
        "limit": serializers.IntegerField(),
        "unread_count": serializers.IntegerField(),
        "results": serializers.ListField(child=serializers.DictField()),
    },
)

NotificationReadAllSchema = inline_serializer(
    name="ToutLire",
    fields={
        "count": serializers.IntegerField(),
        "detail": serializers.CharField(),
    },
)

# ---------- Employés ----------
EmployeeListSchema = inline_serializer(
    name="Employes",
    fields={
        "count": serializers.IntegerField(),
        "results": serializers.ListField(child=serializers.DictField()),
    },
)

# ---------- Suggestions ----------
SuggestionSchema = inline_serializer(
    name="Suggestions",
    fields={
        "results": serializers.ListField(
            child=inline_serializer(
                name="Suggestion",
                fields={
                    "label": serializers.CharField(),
                    "sub": serializers.CharField(allow_blank=True),
                    "value": serializers.CharField(),
                },
            )
        )
    },
)

# ---------- Scanner ----------
ScanConfigSchema = inline_serializer(
    name="ConfigScanner",
    fields={
        "scanner_enabled": serializers.BooleanField(),
        "can_manage_stock": serializers.BooleanField(),
        "can_add_products": serializers.BooleanField(),
        "can_edit_products": serializers.BooleanField(),
        "modes": serializers.ListField(child=serializers.CharField()),
        "default_mode": serializers.CharField(),
    },
)

ScanLookupSchema = inline_serializer(
    name="ScanProduit",
    fields={
        "found": serializers.BooleanField(),
        "uuid": serializers.CharField(required=False),
        "id": serializers.IntegerField(required=False),
        "name": serializers.CharField(required=False),
        "sku": serializers.CharField(required=False),
        "barcode": serializers.CharField(required=False),
        "category": serializers.CharField(required=False),
        "stock": serializers.IntegerField(required=False),
        "sale_price": serializers.CharField(required=False),
        "level": serializers.CharField(required=False),
        "code": serializers.CharField(required=False),
        "message": serializers.CharField(required=False),
    },
)

ScanBatchResultSchema = inline_serializer(
    name="ScanLot",
    fields={
        "ok": serializers.BooleanField(),
        "kind": serializers.CharField(),
        "count": serializers.IntegerField(),
        "items": serializers.ListField(child=serializers.DictField()),
    },
)

# ---------- Synchronisation ----------
SyncStatusSchema = inline_serializer(
    name="SyncEtat",
    fields={
        "status": serializers.CharField(),
        "shop_uuid": serializers.CharField(),
        "shop_name": serializers.CharField(),
        "server_time": serializers.DateTimeField(),
        "unread_count": serializers.IntegerField(),
        "rejected_count": serializers.IntegerField(),
        "last_cursor": serializers.CharField(),
    },
)

# Chaque entité est renvoyée dans son propre tableau ; une liste vide est
# valide, la forme exacte est décrite dans docs/SYNC.md.
_SYNC_ENTITIES = (
    "shop",
    "categories",
    "products",
    "movements",
    "notifications",
    "memberships",
)

SyncPullSchema = inline_serializer(
    name="SyncPull",
    fields={
        "cursor": serializers.CharField(),
        "has_more": serializers.BooleanField(),
        "truncated": serializers.DictField(),
        "counts": serializers.DictField(),
        "profile": serializers.DictField(required=False),
        "server_time": serializers.DateTimeField(),
        **{name: serializers.ListField(child=serializers.DictField(), required=False)
           for name in _SYNC_ENTITIES if name != "shop"},
        "shop": serializers.DictField(required=False, allow_null=True),
    },
)

OperationResultSchema = inline_serializer(
    name="SyncResultatOperation",
    fields={
        "op_id": serializers.CharField(),
        "status": serializers.CharField(),
        "entity": serializers.CharField(required=False),
        "uuid": serializers.CharField(required=False),
        "server": OpenApiTypes.OBJECT,
        "warning": serializers.CharField(required=False, allow_null=True),
        "adjustment": serializers.DictField(required=False),
        "reason_code": serializers.CharField(required=False),
        "reason": serializers.CharField(required=False),
        "suggestion": serializers.DictField(required=False),
        "replayed": serializers.BooleanField(required=False),
    },
)

SyncPushSchema = inline_serializer(
    name="SyncPushReponse",
    fields={
        "results": serializers.ListField(child=OperationResultSchema),
        "applied": serializers.IntegerField(),
        "with_warning": serializers.IntegerField(),
        "rejected": serializers.IntegerField(),
        "server_time": serializers.DateTimeField(),
    },
)

SyncPhotoSchema = inline_serializer(
    name="SyncPhoto",
    fields={
        "entity": serializers.CharField(),
        "server": serializers.DictField(),
        "detail": serializers.CharField(required=False),
    },
)

SyncOperationsSchema = inline_serializer(
    name="SyncJournal",
    fields={
        "count": serializers.IntegerField(),
        "hint": serializers.CharField(),
        "results": serializers.ListField(child=serializers.DictField()),
    },
)