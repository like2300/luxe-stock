"""Support de la synchronisation hors ligne : uuid, updated_at, deleted_at.

Le `uuid` est ajouté sans contrainte unique, rempli ligne par ligne, puis la
contrainte est posée. C'est indispensable : ajouter d'un coup `unique=True`
donnerait la même valeur à toutes les lignes existantes et la migration
échouerait.

Les contraintes d'unicité sku / barcode / nom de catégorie deviennent
conditionnelles (`deleted_at IS NULL`) pour qu'une ligne supprimée logiquement
libère sa valeur.
"""

import uuid

from django.db import migrations, models
from django.db.models import F
from django.utils import timezone

# (modèle, champ source pour updated_at)
_BACKFILL_FROM_CREATED_AT = ("product", "stockmovement", "notification")


def add_uuid_without_unique(apps, schema_editor):
    pass


def fill_uuids(apps, schema_editor):
    for model_name in (
        "shop", "membership", "profile",
        "category", "product", "notification", "stockmovement",
    ):
        model = apps.get_model("core", model_name)
        for obj in model.objects.all().iterator():
            obj.uuid = uuid.uuid4()
            obj.save(update_fields=["uuid"])


def backfill_updated_at(apps, schema_editor):
    for model_name in _BACKFILL_FROM_CREATED_AT:
        model = apps.get_model("core", model_name)
        model.objects.update(updated_at=F("created_at"))


def reverse_uuids(apps, schema_editor):
    """Retour arrière : on remet les lignes à la date du jour."""
    for model_name in ("shop", "membership", "profile",
                       "category", "product", "notification", "stockmovement"):
        model = apps.get_model("core", model_name)
        model.objects.update(updated_at=timezone.now())


UUID_FIELD = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name="UUID")
UPDATED_FIELD = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
DELETED_FIELD = models.DateTimeField(
    blank=True, db_index=True, null=True, verbose_name="Supprimé le"
)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_shop_barcode_field_enabled"),
    ]

    operations = [
        # Les anciennes contraintes sont remplacées plus bas par des versions
        # conditionnelles qui ignorent les lignes supprimées logiquement.
        migrations.RemoveConstraint(
            model_name="product",
            name="uniq_barcode_per_shop",
        ),
        migrations.AlterUniqueTogether(name="category", unique_together=set()),
        migrations.AlterUniqueTogether(name="product", unique_together=set()),

        # 1. uuid provisoirement non unique, puis remplissage, puis unique.
        migrations.AddField(model_name="category", name="uuid", field=UUID_FIELD),
        migrations.AddField(model_name="membership", name="uuid", field=UUID_FIELD),
        migrations.AddField(model_name="notification", name="uuid", field=UUID_FIELD),
        migrations.AddField(model_name="product", name="uuid", field=UUID_FIELD),
        migrations.AddField(model_name="profile", name="uuid", field=UUID_FIELD),
        migrations.AddField(model_name="shop", name="uuid", field=UUID_FIELD),
        migrations.AddField(model_name="stockmovement", name="uuid", field=UUID_FIELD),

        # 2. Horodatage de modification et suppression logique.
        migrations.AddField(model_name="category", name="updated_at", field=UPDATED_FIELD),
        migrations.AddField(model_name="membership", name="updated_at", field=UPDATED_FIELD),
        migrations.AddField(model_name="notification", name="updated_at", field=UPDATED_FIELD),
        migrations.AddField(model_name="product", name="updated_at", field=UPDATED_FIELD),
        migrations.AddField(model_name="shop", name="updated_at", field=UPDATED_FIELD),
        migrations.AddField(model_name="stockmovement", name="updated_at", field=UPDATED_FIELD),

        migrations.AddField(model_name="category", name="deleted_at", field=DELETED_FIELD),
        migrations.AddField(model_name="notification", name="deleted_at", field=DELETED_FIELD),
        migrations.AddField(model_name="product", name="deleted_at", field=DELETED_FIELD),
        migrations.AddField(model_name="stockmovement", name="deleted_at", field=DELETED_FIELD),

        migrations.RunPython(add_uuid_without_unique, migrations.RunPython.noop),
        migrations.RunPython(fill_uuids, reverse_uuids),
        migrations.RunPython(backfill_updated_at, reverse_uuids),

        # 3. La contrainte unique peut maintenant être posée.
        migrations.AlterField(
            model_name="category", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="membership", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="notification", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="product", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="profile", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="shop", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="stockmovement", name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),

        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at__isnull", True)),
                fields=("shop", "name"),
                name="uniq_category_name_per_shop_live",
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at__isnull", True)),
                fields=("shop", "sku"),
                name="uniq_sku_per_shop_live",
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(
                condition=models.Q(models.Q(("barcode", ""), _negated=True),
                                   ("deleted_at__isnull", True)),
                fields=("shop", "barcode"),
                name="uniq_barcode_per_shop_live",
            ),
        ),
    ]