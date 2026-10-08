"""Synchronisation hors ligne : pull, push, idempotence, conflits, isolation.

Ces tests sont la garde-fou du mode hors ligne : une erreur ici se traduit par
du stock perdu ou, pire, du stock belonging a une autre boutique.
"""

import uuid as uuid_lib

from django.test import TestCase

from core.models import (
    Category,
    Membership,
    Notification,
    Product,
    Shop,
    StockMovement,
)

from .factories import api_client_for, make_employee, make_owner_shop, make_product


def op(entity, op_type, payload=None, row_uuid=None, op_id=None):
    """Une operation de la file hors ligne.

    `uuid` identifie la ligne visee et vit au niveau de l'operation, pas dans la
    charge utile : c'est la forme documentee dans docs/SYNC.md.
    """
    operation = {
        "op_id": str(op_id or uuid_lib.uuid4()),
        "entity": entity,
        "type": op_type,
        "payload": payload or {},
    }
    if row_uuid is not None:
        operation["uuid"] = str(row_uuid)
    return operation


class SyncStatusTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)

    def test_status_is_reachable(self):
        response = self.client.get("/api/v1/sync/status/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("server_time", response.data)

    def test_status_requires_authentication(self):
        from .factories import anon_client

        self.assertEqual(anon_client().get("/api/v1/sync/status/").status_code, 401)


class SyncPullTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.category = Category.objects.create(shop=self.shop, name="Boissons")
        self.cola = make_product(
            self.shop, name="Cola", quantity=10, category=self.category, sku="COLA"
)

    def test_full_pull_without_cursor(self):
        response = self.client.get("/api/v1/sync/pull/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([row["name"] for row in response.data["products"]], ["Cola"])
        self.assertEqual(len(response.data["categories"]), 1)
        self.assertIsNotNone(response.data["shop"])
        self.assertEqual(response.data["counts"]["product"], 1)

    def test_pull_returns_an_opaque_cursor(self):
        """Le curseur est une chaine unique : le client n'a pas a le comprendre."""
        cursor = self.client.get("/api/v1/sync/pull/").data["cursor"]
        self.assertIsInstance(cursor, str)
        self.assertTrue(cursor)

    def test_pull_returns_only_rows_changed_since_the_cursor(self):
        first = self.client.get("/api/v1/sync/pull/").data["cursor"]
        self.cola.quantity = 44
        self.cola.save(update_fields=["quantity", "updated_at"])
        rows = self.client.get("/api/v1/sync/pull/", {"cursor": first}).data["products"]
        self.assertEqual([row["quantity"] for row in rows], [44])

    def test_incremental_pull_returns_only_new_rows(self):
        first = self.client.get("/api/v1/sync/pull/").data["cursor"]
        make_product(self.shop, name="Jus", quantity=3, sku="JUS")

        second = self.client.get("/api/v1/sync/pull/", {"cursor": first}).data
        self.assertEqual([row["name"] for row in second["products"]], ["Jus"])
        self.assertEqual(second["counts"]["product"], 1)

    def test_pull_is_strictly_read_only(self):
        """Le pull ne touche jamais au stock."""
        self.client.get("/api/v1/sync/pull/")
        self.cola.refresh_from_db()
        self.assertEqual(self.cola.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_soft_deleted_product_is_published_as_deleted(self):
        """Sans cela, l'app garderait un produit supprime a l'ecran pour toujours."""
        self.cola.soft_delete()
        rows = self.client.get("/api/v1/sync/pull/").data["products"]
        self.assertEqual(len(rows), 1)
        self.assertIsNotNone(rows[0]["deleted_at"])

    def test_pull_is_scoped_to_the_shop(self):
        _o, other = make_owner_shop("autre", "Autre Boutique")
        make_product(other, name="Secret", quantity=99)
        rows = api_client_for(self.owner).get("/api/v1/sync/pull/").data["products"]
        self.assertEqual([row["name"] for row in rows], ["Cola"])

    def test_limit_truncates_and_reports_more(self):
        for i in range(6):
            make_product(self.shop, name=f"P{i}", quantity=1, sku=f"S{i}")
        response = self.client.get("/api/v1/sync/pull/", {"limit": 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["products"]), 3)
        self.assertTrue(response.data["has_more"])

    def test_invalid_cursor_is_refused(self):
        response = self.client.get("/api/v1/sync/pull/", {"cursor": "pas-un-curseur"})
        self.assertEqual(response.status_code, 400)


class SyncPushTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.cola = make_product(self.shop, name="Cola", quantity=10, sku="COLA")

    def push(self, operations):
        return self.client.post(
            "/api/v1/sync/push/", {"operations": operations}, format="json"
        )

    def test_create_product(self):
        response = self.push([
            op("product", "create", {"name": "Jus", "sku": "JUS", "quantity": 2})
        ])
        self.assertEqual(response.status_code, 200, response.data)
        result = response.data["results"][0]
        self.assertEqual(result["status"], "applied")
        self.assertTrue(Product.objects.filter(sku="JUS").exists())

    def test_movement_updates_stock(self):
        response = self.push([
            op("movement", "movement", {"product": str(self.cola.uuid), "kind": "OUT",
                                        "quantity": 3, "note": "Vente"})
        ])
        self.assertEqual(response.data["results"][0]["status"], "applied")
        self.cola.refresh_from_db()
        self.assertEqual(self.cola.quantity, 7)

    def test_out_above_stock_is_truncated_and_warned(self):
        response = self.push([
            op("movement", "movement", {"product": str(self.cola.uuid), "kind": "OUT",
                                        "quantity": 50})
        ])
        result = response.data["results"][0]
        self.assertEqual(result["status"], "applied_with_warning")
        self.cola.refresh_from_db()
        self.assertEqual(self.cola.quantity, 0)

    def test_replaying_an_op_id_changes_nothing(self):
        """Reponse perdue cote reseau : le rejeu doit etre sans effet."""
        operation = op("movement", "movement",
                       {"product": str(self.cola.uuid), "kind": "OUT", "quantity": 2})

        first = self.push([operation]).data["results"][0]
        second = self.push([operation]).data["results"][0]

        self.cola.refresh_from_db()
        self.assertEqual(self.cola.quantity, 8)
        self.assertEqual(StockMovement.objects.count(), 1)
        self.assertFalse(first.get("replayed"))
        self.assertTrue(second.get("replayed"))
        # Le resultat rejoue est le meme, a l'indicateur pres.
        self.assertEqual(first["status"], second["status"])
        self.assertEqual(first["server"], second["server"])

    def test_same_op_id_from_two_users_does_not_leak(self):
        """L'idempotence est cloisonnee par utilisateur."""
        other, _membership = make_employee(self.shop, "bob", can_manage_stock=True)
        operation = op("movement", "movement",
                       {"product": str(self.cola.uuid), "kind": "IN", "quantity": 1})

        self.push([operation])
        response = api_client_for(other).post(
            "/api/v1/sync/push/", {"operations": [operation]}, format="json"
        )
        self.assertEqual(response.data["results"][0]["status"], "applied")
        self.assertEqual(StockMovement.objects.count(), 2)

    def test_missing_permission_is_rejected(self):
        viewer, _ = make_employee(self.shop, "liseur")
        response = api_client_for(viewer).post(
            "/api/v1/sync/push/",
            {"operations": [op("movement", "movement",
                               {"product": str(self.cola.uuid), "kind": "IN",
                                "quantity": 1})]},
format="json",
        )
        result = response.data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "permission_denied")

    def test_one_failure_does_not_block_the_others(self):
        response = self.push([
            op("movement", "movement", {"product": "uuid-inexistant", "kind": "IN",
                                        "quantity": 1}),
            op("movement", "movement", {"product": str(self.cola.uuid), "kind": "IN",
                                        "quantity": 4}),
        ])
        statuses = [r["status"] for r in response.data["results"]]
        self.assertEqual(statuses, ["rejected", "applied"])
        self.cola.refresh_from_db()
        self.assertEqual(self.cola.quantity, 14)

    def test_unknown_operation_type_is_discarded(self):
        response = self.push([op("produit", "faire", {"name": "x"})])
        result = response.data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "bad_payload")

    def test_operation_without_uuid_row_on_create_is_fine(self):
        """A la creation, le client n'a pas encore d'uuid local."""
        result = self.push([
op("product", "create", {"name": "Jus", "sku": "JUS"})
        ]).data["results"][0]
        self.assertEqual(result["status"], "applied")
        self.assertIsNotNone(result["uuid"])

    def test_delete_product_is_logical(self):
        result = self.push([
            op("product", "delete", row_uuid=self.cola.uuid)
        ]).data["results"][0]
        self.assertEqual(result["status"], "applied")
        self.assertFalse(Product.objects.filter(pk=self.cola.pk).exists())
        self.assertTrue(Product.all_objects.filter(pk=self.cola.pk).exists())

    def test_empty_batch_is_refused(self):
        response = self.push([])
        self.assertEqual(response.status_code, 400)

    def test_batch_above_the_limit_is_refused(self):
        operations = [op("product", "create", {"name": f"P{i}"}) for i in range(201)]
        self.assertEqual(self.push(operations).status_code, 400)


class SyncConflictTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.cola = make_product(self.shop, name="Cola", quantity=10, sku="COLA")

    def push(self, operations):
        return self.client.post(
            "/api/v1/sync/push/", {"operations": operations}, format="json"
        )

    def test_movement_on_a_deleted_product_is_rejected(self):
        """Regle 4 : le produit a disparu entre-temps, on ne sort pas un stock fantome."""
        self.cola.soft_delete()
        result = self.push([
            op("movement", "movement", {"product": str(self.cola.uuid), "kind": "OUT",
                                        "quantity": 1})
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "product_deleted")
        self.assertEqual(result["suggestion"]["action"], "discard_or_create")
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_duplicate_sku_created_offline_is_rejected(self):
        result = self.push([
            op("product", "create", {"name": "Cola bis", "sku": "COLA"})
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(Product.objects.filter(sku="COLA").count(), 1)

    def test_duplicate_barcode_created_offline_is_rejected(self):
        make_product(self.shop, name="Autre", sku="AUTRE", barcode="1234567890123")
        result = self.push([
            op("product", "create", {"name": "Copie", "barcode": "1234567890123"})
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")

    def test_adjust_with_a_stale_previous_quantity_warns(self):
        """L'app avait vu 10, le serveur est a 8 : l'ecart est recalcule."""
        self.cola.quantity = 8
        self.cola.save(update_fields=["quantity"])
        result = self.push([
            op("movement", "adjust", {"product": str(self.cola.uuid),
                                      "previous_quantity": 10, "quantity": 4})
        ]).data["results"][0]
        self.assertEqual(result["status"], "applied_with_warning")
        self.cola.refresh_from_db()
        self.assertEqual(self.cola.quantity, 4)

    def test_adjust_records_the_real_server_delta(self):
        """Le mouvement trace doit dire 8 -> 4, pas 10 -> 4."""
        self.cola.quantity = 8
        self.cola.save(update_fields=["quantity"])
        self.push([
            op("movement", "adjust", {"product": str(self.cola.uuid),
                                      "previous_quantity": 10, "quantity": 4})
        ])
        movement = self.cola.movements.get()
        self.assertEqual(movement.quantity, 4)
        self.assertEqual(movement.kind, StockMovement.OUT)

def test_pull_after_push_reflects_the_change(self):
        cursor = self.client.get("/api/v1/sync/pull/").data["cursor"]
        self.push([op("movement", "movement", {"product": str(self.cola.uuid),
                                                "kind": "IN", "quantity": 7})])
        data = self.client.get("/api/v1/sync/pull/", {"cursor": cursor}).data
        self.assertEqual(len(data["movements"]), 1)
        self.assertEqual(len(data["products"]), 1)


class SyncIsolationTests(TestCase):
    """Aucune operation hors ligne ne doit viser une autre boutique."""

    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.stranger, self.home_shop = make_owner_shop("etranger", "Boutique Etrangere")
        self.client = api_client_for(self.stranger)
        self.foreign = make_product(self.shop, name="Cola", quantity=10, sku="COLA")

    def push(self, operations):
        return self.client.post(
            "/api/v1/sync/push/", {"operations": operations}, format="json"
        )

    def test_movement_on_a_foreign_product_uuid_is_rejected(self):
        result = self.push([
            op("movement", "movement", {"product": str(self.foreign.uuid), "kind": "OUT",
                                        "quantity": 1})
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "not_found")
        self.foreign.refresh_from_db()
        self.assertEqual(self.foreign.quantity, 10)

    def test_movement_by_foreign_barcode_is_rejected(self):
        make_product(self.shop, name="Jus", quantity=5, sku="JUS", barcode="5550001112222")
        result = self.push([
            op("movement", "movement", {"product": "5550001112222", "kind": "OUT",
"quantity": 1})
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")

    def test_delete_of_a_foreign_product_is_rejected(self):
        result = self.push([
            op("product", "delete", row_uuid=self.foreign.uuid)
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(Product.objects.filter(pk=self.foreign.pk).exists())

    def test_update_of_a_foreign_product_is_rejected(self):
        """Comme `delete` et `movement` : `not_found`, jamais une erreur Python.

        Un dereferencement sur `None` echouait plus bas, et le filet de securite
        remontait alors le message d'exception dans `reason`.
        """
        result = self.push([
            op("product", "update", {"name": "Piratage"}, row_uuid=self.foreign.uuid)
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "not_found")
        self.foreign.refresh_from_db()
        self.assertEqual(self.foreign.name, "Cola")

    def test_update_of_an_unknown_product_is_rejected(self):
        result = self.push([
            op("product", "update", {"name": "X"}, row_uuid=uuid_lib.uuid4())
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "not_found")

    def test_update_of_a_deleted_product_says_so(self):
        """Mieux que « introuvable » : la suppression est deja connue."""
        deleted = make_product(self.home_shop, name="Jus", quantity=4, sku="JUS")
        deleted.soft_delete()
        result = self.push([
            op("product", "update", {"name": "Renomme"}, row_uuid=deleted.uuid)
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "product_deleted")

    def test_row_uuid_of_another_shop_is_rejected(self):
        """Meme avec un op_id pointant vers une ligne etrangere."""
        result = self.push([
            op("movement", "movement", {"kind": "IN", "quantity": 1},
               row_uuid=self.foreign.uuid)
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_code"], "not_found")
        self.foreign.refresh_from_db()
        self.assertEqual(self.foreign.quantity, 10)

    def test_category_of_another_shop_is_rejected(self):
        foreign_category = Category.objects.create(shop=self.shop, name="Etrangere")
        result = self.push([
            op("product", "create", {"name": "X", "category": str(foreign_category.uuid)})
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")

def test_membership_of_another_shop_is_rejected(self):
        _o, other = make_owner_shop("autre", "Autre")
        member = Membership.objects.exclude(user=other.owner).first()
        result = self.push([
            op("membership", "update",
               {"permissions": {"can_add_products": True}}, row_uuid=member.uuid)
        ]).data["results"][0]
        self.assertEqual(result["status"], "rejected")


class SyncOperationsJournalTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.cola = make_product(self.shop, name="Cola", quantity=10, sku="COLA")

    def test_journal_records_applied_and_rejected(self):
        self.client.post(
            "/api/v1/sync/push/",
            {"operations": [
                op("movement", "movement", {"product": str(self.cola.uuid), "kind": "IN",
                                            "quantity": 1}),
                op("movement", "movement", {"product": "inexistant", "kind": "IN",
                                            "quantity": 1}),
            ]},
            format="json",
        )
        response = self.client.get("/api/v1/sync/operations/")
        self.assertEqual(response.status_code, 200)
        statuses = {row["status"] for row in response.data["results"]}
        self.assertEqual(statuses, {"applied", "rejected"})

    def test_journal_is_scoped_to_the_user(self):
        employee, _ = make_employee(self.shop, "bob", can_manage_stock=True)
        self.client.post(
            "/api/v1/sync/push/",
            {"operations": [op("movement", "movement", {"product": str(self.cola.uuid),
                                                        "kind": "IN", "quantity": 1})]},
            format="json",
        )
        response = api_client_for(employee).get("/api/v1/sync/operations/")
        self.assertEqual(response.data["count"], 0)

    def test_journal_filters_by_status(self):
        self.client.post(
            "/api/v1/sync/push/",
            {"operations": [op("movement", "movement", {"product": "inexistant",
                                                        "kind": "IN", "quantity": 1})]},
            format="json",
        )
        response = self.client.get("/api/v1/sync/operations/", {"status": "applied"})
        self.assertEqual(response.data["count"], 0)
        response = self.client.get("/api/v1/sync/operations/", {"status": "rejected"})
        self.assertEqual(response.data["count"], 1)

    def test_journal_survives_a_negative_limit(self):
        """`limit=-1` faisait une indexation negative : le journal levait un 500."""
        for limit in (-1, -100, 0, "beaucoup"):
            response = self.client.get("/api/v1/sync/operations/", {"limit": limit})
            self.assertEqual(response.status_code, 200, limit)


class SyncShopUpdateTests(TestCase):
    """Mise a jour de la boutique par le push.

    Le push ne fait pas passer la charge utile par un serializer DRF : c'est au
    gestionnaire qu'il revient de borner et de convertir chaque champ, sinon une
    valeur mal typee echoue dans `save()` et casse la transaction du lot.
    """

    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)

    def push_shop(self, payload):
        return self.client.post(
            "/api/v1/sync/push/",
            {"operations": [op("shop", "update", payload, row_uuid=self.shop.uuid)]},
            format="json",
        ).data["results"][0]

    def test_booleans_accept_the_json_spellings(self):
        for raw in (False, 0, "0", "false", "False", "non", "off"):
            result = self.push_shop({"scanner_enabled": raw})
            self.assertEqual(result["status"], "applied", raw)
            self.shop.refresh_from_db()
            self.assertFalse(self.shop.scanner_enabled, raw)
        for raw in (True, 1, "1", "true", "True", "oui", "on"):
            result = self.push_shop({"barcode_field_enabled": raw})
            self.assertEqual(result["status"], "applied", raw)
            self.shop.refresh_from_db()
            self.assertTrue(self.shop.barcode_field_enabled, raw)

    def test_an_unreadable_boolean_is_rejected_not_fatal(self):
        """Le refus doit rester dans le resultat de l'operation, pas casser le lot."""
        response = self.client.post(
            "/api/v1/sync/push/",
            {"operations": [
                op("shop", "update", {"scanner_enabled": "peut-etre"},
                   row_uuid=self.shop.uuid),
                op("product", "create", {"name": "Jus", "sku": "JUS"}),
            ]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        first, second = response.data["results"]
        self.assertEqual(first["reason_code"], "invalid_field")
        self.assertEqual(second["status"], "applied")
        self.assertTrue(Product.objects.filter(sku="JUS").exists())

    def test_a_too_long_name_is_bounded(self):
        """Sans borne, SQLite accepte 300 caracteres dans une colonne de 120."""
        result = self.push_shop({"name": "X" * 300})
        self.assertEqual(result["status"], "applied")
        self.shop.refresh_from_db()
        self.assertEqual(len(self.shop.name), Shop._meta.get_field("name").max_length)

    def test_an_empty_name_is_still_refused(self):
        result = self.push_shop({"name": "   "})
        self.assertEqual(result["reason_code"], "invalid_field")

    def test_an_invalid_colour_is_refused(self):
        result = self.push_shop({"primary_color": "bleu"})
        self.assertEqual(result["reason_code"], "invalid_field")

    def test_only_the_owner_updates_the_shop(self):
        employee, _ = make_employee(self.shop, "bob")
        result = api_client_for(employee).post(
            "/api/v1/sync/push/",
            {"operations": [op("shop", "update", {"name": "Piratee"},
                               row_uuid=self.shop.uuid)]},
            format="json",
        ).data["results"][0]
        self.assertEqual(result["reason_code"], "permission_denied")
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.name, "Ma Boutique")


class SyncNotificationTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.cola = make_product(self.shop, name="Cola", quantity=10, sku="COLA")
        self.notification = Notification.objects.create(
            shop=self.shop, product=self.cola, kind=Notification.LOW_STOCK,
            label="Stock bas", message="Stock bas", sound_code="low",
)

    def test_read_notification_offline(self):
        result = self.client.post(
            "/api/v1/sync/push/",
            {"operations": [op("notification", "notification_read",
                               row_uuid=self.notification.uuid)]},
            format="json",
        ).data["results"][0]
        self.assertEqual(result["status"], "applied")
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_read_all_notifications(self):
        result = self.client.post(
            "/api/v1/sync/push/",
            {"operations": [op("notification", "notification_read_all", {})]},
            format="json",
        ).data["results"][0]
        self.assertEqual(result["status"], "applied")
        self.assertEqual(self.shop.notifications.filter(is_read=False).count(), 0)

    def test_clear_notifications_is_logical(self):
        self.client.post(
            "/api/v1/sync/push/",
            {"operations": [op("notification", "notification_clear", {})]},
            format="json",
        )
        self.assertEqual(self.shop.notifications.count(), 0)
        self.assertEqual(Notification.all_objects.filter(shop=self.shop).count(), 1)
