"""Journal des opérations de synchronisation.

Le `push` est idempotent : chaque `op_id` est enregistré avec le résultat
exactement renvoyé au client. Rejouer le même `op_id` ne modifie rien en base
et renvoie la réponse d'origine, ce qui rend la file "outbox" du client sûr
en cas de réponse perdue (voir docs/SYNC.md § 4.3).

L'unicité porte sur le couple `(user, op_id)` : deux boutiques peuvent émettre
la même opération, et un `op_id` global ferait échouer le push de l'une sous
le rejet de l'autre.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class SyncOperation(models.Model):
    APPLIED = "applied"
    APPLIED_WITH_WARNING = "applied_with_warning"
    REJECTED = "rejected"

    STATUS_CHOICES = [
        (APPLIED, "Appliquée"),
        (APPLIED_WITH_WARNING, "Appliquée avec avertissement"),
        (REJECTED, "Rejetée"),
    ]

    op_id = models.UUIDField("Identifiant de l'opération")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sync_operations")

    entity = models.CharField("Entité", max_length=20)
    op_type = models.CharField("Type", max_length=24)

    status = models.CharField("Statut", max_length=24, choices=STATUS_CHOICES)
    reason_code = models.CharField("Code de rejet", max_length=32, blank=True)
    reason = models.CharField("Motif", max_length=250, blank=True)

    # Réponse renvoyée au client, rejouée telle quelle.
    result = models.JSONField("Résultat", default=dict)
    # Dernière charge utile reçue, conservée pour le journal des rejets.
    payload = models.JSONField("Charge utile", default=dict, blank=True)

    device_id = models.CharField("Appareil", max_length=64, blank=True)

    created_at = models.DateTimeField("Reçue le", auto_now_add=True)
    processed_at = models.DateTimeField("Traitée le", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Opération de synchronisation"
        verbose_name_plural = "Opérations de synchronisation"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]
        constraints = [
            # L'`op_id` est produit par l'appareil : deux membres peuvent
            # theoriquement envoyer le meme. La portee de l'idempotence est
            # l'utilisateur, jamais le serveur entier.
            models.UniqueConstraint(fields=["user", "op_id"], name="uniq_sync_op_per_user"),
        ]

    def __str__(self):
        return f"{self.op_id} {self.entity}/{self.op_type} {self.status}"


def purge_old_operations(days=30):
    """Supprime le journal des opérations traitées depuis plus de `days` jours."""
    limit = timezone.now() - timedelta(days=days)
    deleted, _ = SyncOperation.objects.filter(processed_at__lt=limit).delete()
    return deleted