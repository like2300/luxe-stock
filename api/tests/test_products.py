"""Produits : liste, filtres, creation, modification, suppression logique.

Ces tests verrouillent deux choses : la parite avec le web (mouvements traces,
seuils, niveaux) et l'isolation entre boutiques.
"""

from django.test import TestCase

from core.models import Notification, Product, StockMovement

from .factories import (
    anon_client,
    api_client_for,
    make_category,
    make_employee,
    make_owner_shop,
    make_product,
)


class ProductListTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.category = make_category(self.shop, "Boissons")
        self.cola = make_product(
            self.shop, name="Cola", quantity=12, category=self.category, sku="COLA"
        )
        self.eau = make_product(self.shop, name="Eau", quantity=2, sku="EAU")

    def test_list_returns_envelope(self):
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_list_is_scoped_to_the_shop(self):
        """Un produit d'une autre boutique n'apparait jamais."""
        _other_owner, other_shop = make_owner_shop("autre", "Autre Boutique")
        make_product(other_shop, name="Secret", quantity=99)
        response = self.client.get("/api/v1/products/")
        names = [row["name"] for row in response.data["results"]]
        self.assertNotIn("Secret", names)

    def test_search_filter(self):
        response = self.client.get("/api/v1/products/", {"q": "col"})
        self.assertEqual([row["name"] for row in response.data["results"]], ["Cola"])

    def test_level_filter_rupture(self):
        make_product(self.shop, name="Zero", quantity=0, sku="ZERO")
        response = self.client.get("/api/v1/products/", {"level": "rupture"})
        self.assertEqual([row["name"] for row in response.data["results"]], ["Zero"])

    def test_low_filter_uses_each_product_threshold(self):
        """« Stock bas » suit le seuil de chaque produit, pas un seuil global."""
        make_product(self.shop, name="Sous seuil", quantity=4, sku="SEUIL", alert_threshold=5)
        make_product(self.shop, name="Juste au seuil", quantity=6, sku="JUSTE",
                     alert_threshold=5)
        response = self.client.get("/api/v1/products/", {"level": "bas"})
        self.assertEqual(
            sorted(row["name"] for row in response.data["results"]),
            ["Eau", "Sous seuil"],
        )

    def test_ok_filter_excludes_low_products(self):
        response = self.client.get("/api/v1/products/", {"level": "ok"})
        self.assertEqual([row["name"] for row in response.data["results"]], ["Cola"])

    def test_soft_deleted_products_are_hidden_from_the_list(self):
        Product.all_objects.filter(pk=self.eau.pk).update(deleted_at="2026-01-01T00:00:00Z")
        response = self.client.get("/api/v1/products/")
        self.assertEqual([row["name"] for row in response.data["results"]], ["Cola"])


class ProductWriteTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.category = make_category(self.shop, "Boissons")

    def test_create_records_an_initial_movement(self):
        """Le stock initial doit laisser une trace, comme le formulaire du web."""
        response = self.client.post(
            "/api/v1/products/",
            {"name": "Cola", "sku": "COLA", "quantity": 10, "category": str(self.category.uuid)},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        product = Product.objects.get(sku="COLA")
        self.assertEqual(product.quantity, 10)
        movement = product.movements.get()
        self.assertEqual(movement.kind, StockMovement.IN)
        self.assertEqual(movement.quantity, 10)
        self.assertEqual(movement.note, "Stock initial")

    def test_create_notifies_the_shop(self):
        self.client.post(
            "/api/v1/products/", {"name": "Cola", "quantity": 3}, format="json"
        )
        self.assertTrue(
            self.shop.notifications.filter(kind=Notification.PRODUCT_ADDED).exists()
        )

    def test_update_quantity_is_traced_as_a_movement(self):
        """Changer la quantité par l'API doit laisser le meme historique que le web."""
        product = make_product(self.shop, name="Cola", quantity=10, sku="COLA")
        response = self.client.put(
            f"/api/v1/products/{product.uuid}/",
            {"name": "Cola", "sku": "COLA", "quantity": 4, "alert_threshold": 5},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        product.refresh_from_db()
        self.assertEqual(product.quantity, 4)
        movement = product.movements.get()
        self.assertEqual(movement.kind, StockMovement.OUT)
        self.assertEqual(movement.quantity, 6)

    def test_update_without_quantity_does_not_invent_a_movement(self):
        product = make_product(self.shop, name="Cola", quantity=10, sku="COLA")
        response = self.client.patch(
            f"/api/v1/products/{product.uuid}/", {"name": "Cola 33cl"}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(product.movements.count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.quantity, 10)

    def test_duplicate_sku_is_refused_with_the_web_message(self):
        make_product(self.shop, name="Cola", sku="COLA")
        response = self.client.post(
            "/api/v1/products/", {"name": "Autre", "sku": "COLA"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("déjà", response.data["errors"]["sku"])

    def test_duplicate_barcode_is_refused(self):
        make_product(self.shop, name="Cola", barcode="1234567890123")
        response = self.client.post(
            "/api/v1/products/",
            {"name": "Autre", "barcode": "1234567890123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_category_from_another_shop_is_refused(self):
        _o, other = make_owner_shop("autre", "Autre Boutique")
        foreign = make_category(other, "Etrangere")
        response = self.client.post(
            "/api/v1/products/",
            {"name": "Cola", "category": str(foreign.uuid)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("n'existe pas", response.data["errors"]["category"])

    def test_soft_delete_keeps_the_row_and_frees_the_sku(self):
        product = make_product(self.shop, name="Cola", sku="COLA", barcode="111")
        response = self.client.delete(f"/api/v1/products/{product.uuid}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Produit supprimé.")

        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
        self.assertTrue(Product.all_objects.filter(pk=product.pk).exists())

        # Le SKU est de nouveau disponible.
        again = self.client.post(
            "/api/v1/products/", {"name": "Cola neuf", "sku": "COLA"}, format="json"
        )
        self.assertEqual(again.status_code, 201, again.data)

    def test_bulk_delete(self):
        products = [make_product(self.shop, name=f"P{i}", sku=f"S{i}") for i in range(3)]
        response = self.client.post(
            "/api/v1/products/bulk_delete/",
            {"uuids": [str(p.uuid) for p in products]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["detail"], "3 produit(s) supprimé(s).")
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Product.all_objects.count(), 3)


class ProductIsolationTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.stranger, _ = make_owner_shop("etranger", "Boutique Etrangere")
        self.client = api_client_for(self.stranger)
        self.product = make_product(self.shop, name="Cola", quantity=10, sku="COLA")

    def test_cannot_read_another_shop_product(self):
        response = self.client.get(f"/api/v1/products/{self.product.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_cannot_update_another_shop_product(self):
        response = self.client.patch(
            f"/api/v1/products/{self.product.uuid}/", {"name": "Piraté"}, format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Cola")

    def test_cannot_delete_another_shop_product(self):
        response = self.client.delete(f"/api/v1/products/{self.product.uuid}/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Product.objects.count(), 1)

    def test_bulk_delete_ignores_foreign_uuids(self):
        response = self.client.post(
            "/api/v1/products/bulk_delete/",
            {"uuids": [str(self.product.uuid)]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "0 produit(s) supprimé(s).")
        self.assertEqual(Product.objects.count(), 1)


class ProductPermissionTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.viewer, _ = make_employee(self.shop, "liseur")
        self.editor, _ = make_employee(
            self.shop, "editeur", can_edit_products=True, can_add_products=True
        )
        self.category = make_category(self.shop, "Boissons")

    def test_employee_without_permission_cannot_create(self):
        response = api_client_for(self.viewer).post(
            "/api/v1/products/", {"name": "Cola"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_employee_without_permission_cannot_delete(self):
        product = make_product(self.shop, name="Cola", sku="COLA")
        response = api_client_for(self.viewer).delete(f"/api/v1/products/{product.uuid}/")
        self.assertEqual(response.status_code, 403)

    def test_employee_with_permission_can_create(self):
        response = api_client_for(self.editor).post(
            "/api/v1/products/", {"name": "Cola", "sku": "COLA"}, format="json"
        )
        self.assertEqual(response.status_code, 201, response.data)

    def test_anonymous_is_refused(self):
        self.assertEqual(anon_client().get("/api/v1/products/").status_code, 401)