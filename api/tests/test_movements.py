"""Mouvements et notifications : la logique métier reste celle du web."""

from django.test import TestCase

from core.models import Notification, Product, StockMovement

from .factories import (
    api_client_for,
    make_employee,
    make_owner_shop,
    make_product,
)


class MovementCreateTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.product = make_product(self.shop, name="Cola", quantity=10, sku="COLA")

    def test_entry_updates_stock_and_records_movement(self):
        response = self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "IN", "quantity": 5, "note": "Livraison"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15)
        movement = StockMovement.objects.get()
        self.assertEqual(movement.kind, StockMovement.IN)
        self.assertEqual(movement.note, "Livraison")

    def test_exit_updates_stock(self):
        self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "OUT", "quantity": 4},
            format="json",
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 6)

    def test_crossing_the_threshold_notifies_once(self):
        """Le seuil de 5 est franchi a la sortie ; une deuxieme sortie ne reclame rien."""
        self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "OUT", "quantity": 6},
            format="json",
        )
        lows = self.shop.notifications.filter(kind=Notification.LOW_STOCK)
        self.assertEqual(lows.count(), 1)

        self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "OUT", "quantity": 1},
            format="json",
        )
        self.assertEqual(
            self.shop.notifications.filter(kind=Notification.LOW_STOCK).count(), 1
        )

    def test_out_of_stock_raises_the_alert(self):
        self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "OUT", "quantity": 10},
            format="json",
        )
        self.assertTrue(
            self.shop.notifications.filter(kind=Notification.OUT_OF_STOCK).exists()
        )

    def test_negative_stock_is_refused(self):
        """Le web refuse de descendre sous zero par une sortie."""
        response = self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "OUT", "quantity": 99},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)

    def test_zero_quantity_is_refused(self):
        response = self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "IN", "quantity": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_product_can_be_referenced_by_barcode(self):
        make_product(self.shop, name="Jus", quantity=4, sku="JUS", barcode="5550001112222")
        response = self.client.post(
            "/api/v1/movements/",
            {"product": "5550001112222", "kind": "IN", "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)

    def test_product_from_another_shop_is_refused(self):
        _o, other = make_owner_shop("autre", "Autre Boutique")
        foreign = make_product(other, name="Secret", quantity=5, sku="SEC")
        response = self.client.post(
            "/api/v1/movements/",
            {"product": str(foreign.uuid), "kind": "IN", "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(foreign.movements.count(), 0)

    def test_permission_is_required(self):
        viewer, _ = make_employee(self.shop, "liseur")
        response = api_client_for(viewer).post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "IN", "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class MovementListTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.product = make_product(self.shop, name="Cola", quantity=10, sku="COLA")
        for kind, qty, note in (("IN", 5, "Livraison"), ("OUT", 2, "Vente")):
            self.client.post(
                "/api/v1/movements/",
                {"product": str(self.product.uuid), "kind": kind, "quantity": qty,
                 "note": note},
                format="json",
            )

    def test_list_is_scoped_and_newest_first(self):
        response = self.client.get("/api/v1/movements/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["note"], "Vente")

    def test_type_filter(self):
        response = self.client.get("/api/v1/movements/", {"type": "IN"})
        self.assertEqual([row["note"] for row in response.data["results"]], ["Livraison"])

    def test_search_filter(self):
        response = self.client.get("/api/v1/movements/", {"q": "vente"})
        self.assertEqual(response.data["count"], 1)

    def test_another_shop_sees_nothing(self):
        _o, other = make_owner_shop("autre", "Autre")
        make_product(other, name="Rien", quantity=1, sku="R")
        response = api_client_for(other.owner).get("/api/v1/movements/")
        self.assertEqual(response.data["count"], 0)


class NotificationTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.product = make_product(self.shop, name="Cola", quantity=10, sku="COLA")
        self.client.post(
            "/api/v1/movements/",
            {"product": str(self.product.uuid), "kind": "IN", "quantity": 2},
            format="json",
        )

    def test_feed_lists_notifications(self):
        response = self.client.get("/api/v1/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["results"])
        row = response.data["results"][0]
        self.assertIn("level", row)
        self.assertIn("colors", row)

    def test_unread_filter(self):
        Notification.objects.filter(shop=self.shop).update(is_read=True)
        response = self.client.get("/api/v1/notifications/", {"unread": "1"})
        self.assertEqual(response.data["count"], 0)

    def test_mark_one_as_read(self):
        notification = self.shop.notifications.first()
        response = self.client.post(f"/api/v1/notifications/{notification.uuid}/read/")
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_as_read(self):
        response = self.client.post("/api/v1/notifications/read_all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.shop.notifications.filter(is_read=False).count(), 0)

    def test_clear_is_a_soft_delete(self):
        """« Tout effacer » ne doit pas effacer l'historique cote serveur."""
        kept = Notification.all_objects.filter(shop=self.shop).count()
        self.assertGreater(kept, 0)

        response = self.client.delete("/api/v1/notifications/clear/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.shop.notifications.count(), 0)
        self.assertEqual(Notification.all_objects.filter(shop=self.shop).count(), kept)

    def test_cannot_read_another_shop_notification(self):
        """Un uuid d'une autre boutique doit repondre 404, pas divulguer la ligne."""
        _o, other = make_owner_shop("autre", "Autre")
        foreign = Notification.objects.create(
            shop=other, kind=Notification.LOW_STOCK, label="Bas", message="Bas",
            sound_code="low",
        )
        response = self.client.post(f"/api/v1/notifications/{foreign.uuid}/read/")
        self.assertEqual(response.status_code, 404)
        foreign.refresh_from_db()
        self.assertFalse(foreign.is_read)