"""Scanner, employes, profil et boutique : les ecrans secondaires.

Meme exigence partout : la boutique peut desactiver le scanner, et seul le
proprietaire gere les comptes comme les couleurs.
"""

from django.test import TestCase

from core.models import Membership, Product

from .factories import (
    api_client_for,
    make_employee,
    make_owner_shop,
    make_product,
    make_user,
)


class ShopTests(TestCase):
    def test_create_shop_when_account_has_none(self):
        user = make_user("nouveau")
        response = api_client_for(user).post(
            "/api/v1/shops/", {"name": "Ma Boutique", "currency": "FCFA"}, format="json"
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(Membership.objects.filter(user=user, is_owner=True).exists())

    def test_second_shop_is_refused(self):
        owner, _shop = make_owner_shop()
        response = api_client_for(owner).post(
            "/api/v1/shops/", {"name": "Autre"}, format="json"
        )
        self.assertEqual(response.status_code, 409)

    def test_read_current_shop(self):
        owner, shop = make_owner_shop()
        response = api_client_for(owner).get("/api/v1/shops/current/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uuid"], str(shop.uuid))

    def test_only_the_owner_saves_settings(self):
        owner, shop = make_owner_shop()
        employee, _ = make_employee(shop, "bob", can_view_products=True)
        refused = api_client_for(employee).put(
            "/api/v1/shops/current/", {"name": "Renommee"}, format="json"
        )
        self.assertEqual(refused.status_code, 403)

        accepted = api_client_for(owner).put(
            "/api/v1/shops/current/", {"name": "Renommee"}, format="json"
        )
        self.assertEqual(accepted.status_code, 200, accepted.data)
        shop.refresh_from_db()
        self.assertEqual(shop.name, "Renommee")

    def test_invalid_colour_is_refused(self):
        owner, shop = make_owner_shop()
        response = api_client_for(owner).put(
            "/api/v1/shops/current/", {"primary_color": "rouge"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        shop.refresh_from_db()
        self.assertEqual(shop.primary_color, "#5bc0de")


class DashboardTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.product = make_product(
            self.shop, name="Cola", quantity=3, sku="COLA", cost_price="100"
        )

    def test_dashboard_returns_indicators(self):
        response = self.client.get("/api/v1/dashboard/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["currency"], self.shop.currency)
        self.assertEqual(len(response.data["chart"]["labels"]), 6)
        self.assertEqual(len(response.data["low_products"]), 1)

    def test_dashboard_needs_the_view_permission(self):
        user = make_user("sans-boutique")
        response = api_client_for(user).get("/api/v1/dashboard/")
        self.assertEqual(response.status_code, 409)


class ScanTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.product = make_product(
            self.shop, name="Cola", quantity=8, sku="COLA", barcode="5550001112222"
        )

    def test_lookup_by_barcode(self):
        response = self.client.get("/api/v1/scan/", {"code": "5550001112222"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["found"])
        self.assertEqual(response.data["name"], "Cola")

    def test_lookup_by_sku(self):
        response = self.client.get("/api/v1/scan/", {"code": "COLA"})
        self.assertTrue(response.data["found"])

    def test_unknown_code_offers_creation(self):
        response = self.client.get("/api/v1/scan/", {"code": "0000000000000"})
        self.assertFalse(response.data["found"])

    def test_disabled_scanner_is_refused(self):
        self.shop.scanner_enabled = False
        self.shop.save(update_fields=["scanner_enabled"])
        response = self.client.get("/api/v1/scan/", {"code": "5550001112222"})
        self.assertEqual(response.status_code, 403)

    def test_config_reflects_shop_settings(self):
        response = self.client.get("/api/v1/scan/config/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["scanner_enabled"])

        self.shop.barcode_field_enabled = False
        self.shop.save(update_fields=["barcode_field_enabled"])
        response = self.client.get("/api/v1/scan/config/")
        self.assertFalse(response.data["barcode_field_enabled"])

    def test_batch_is_atomic(self):
        """Une ligne inconnue doit annuler tout le lot."""
        response = self.client.post(
            "/api/v1/scan/movements/",
            {"kind": "OUT", "items": [
                {"code": "5550001112222", "quantity": 1},
                {"code": "code-inconnu", "quantity": 1},
            ]},
            format="json",
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 8)

    def test_batch_applies_every_line(self):
        response = self.client.post(
            "/api/v1/scan/movements/",
            {"kind": "OUT", "items": [
                {"code": "5550001112222", "quantity": 2},
                {"code": "COLA", "quantity": 1},
            ]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["count"], 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 5)

    def test_batch_needs_stock_permission(self):
        employee, _ = make_employee(self.shop, "liseur")
        response = api_client_for(employee).post(
            "/api/v1/scan/movements/",
            {"kind": "OUT", "items": [{"code": "5550001112222", "quantity": 1}]},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class EmployeeTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.employee, self.membership = make_employee(
            self.shop, "bob", can_add_products=True, can_manage_stock=True
        )

    def test_owner_lists_employees_without_themselves(self):
        response = self.client.get("/api/v1/employees/")
        self.assertEqual(response.status_code, 200)
        usernames = [row["username"] for row in response.data["results"]]
        self.assertEqual(usernames, ["bob"])

    def test_employee_cannot_list_employees(self):
        response = api_client_for(self.employee).get("/api/v1/employees/")
        self.assertEqual(response.status_code, 403)

    def test_create_employee(self):
        response = self.client.post(
            "/api/v1/employees/",
            {"username": "carla", "email": "carla@exemple.test", "password": "un-mot-de-passe-1",
             "can_view_products": True, "can_manage_stock": True},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        membership = Membership.objects.get(user__username="carla")
        self.assertEqual(membership.shop, self.shop)
        self.assertTrue(membership.can_manage_stock)
        self.assertFalse(membership.is_owner)

    def test_update_permissions(self):
        response = self.client.put(
            f"/api/v1/employees/{self.membership.uuid}/",
            {"username": "bob", "can_view_products": True, "can_edit_products": True,
             "can_add_products": False, "can_delete_products": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.membership.refresh_from_db()
        self.assertTrue(self.membership.can_delete_products)
        self.assertFalse(self.membership.can_add_products)
        # Une case cochee absente n'est pas « decochee », et une case decochee
        # est bien enregistree : la reponse reflete la nouvelle adhesion.
        self.assertTrue(self.membership.can_manage_stock)
        self.assertIn("Voir les produits", response.data["granted_permissions"])
        self.assertNotIn("Ajouter des produits", response.data["granted_permissions"])

    def test_leaving_the_password_empty_keeps_the_old_one(self):
        response = self.client.put(
            f"/api/v1/employees/{self.membership.uuid}/",
            {"username": "bob", "password": "", "can_view_products": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(self.employee.check_password("motdepasse-tres-long-1"))

    def test_delete_employee(self):
        response = self.client.delete(f"/api/v1/employees/{self.membership.uuid}/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(Membership.objects.filter(pk=self.membership.pk).exists())

    def test_cannot_touch_the_owner_account(self):
        owner_membership = Membership.objects.get(user=self.owner, shop=self.shop)
        response = self.client.delete(f"/api/v1/employees/{owner_membership.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_another_shop_employee_is_not_reachable(self):
        _o, other = make_owner_shop("autre", "Autre")
        foreign, foreign_membership = make_employee(other, "zina")
        response = self.client.delete(f"/api/v1/employees/{foreign_membership.uuid}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Membership.objects.filter(pk=foreign_membership.pk).exists())


class ProfileTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)

    def test_read_profile(self):
        response = self.client.get("/api/v1/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.owner.username)
        self.assertEqual(response.data["role"], "Propriétaire")

    def test_update_phone_and_bio(self):
        response = self.client.put(
            "/api/v1/profile/", {"phone": "+33 6 12 34 56 78", "bio": "Gestionnaire"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["phone"], "+33 6 12 34 56 78")

    def test_bio_is_length_limited(self):
        response = self.client.put(
            "/api/v1/profile/", {"bio": "x" * 300}, format="json"
        )
        self.assertEqual(response.status_code, 400)


class SuggestionTests(TestCase):
    def setUp(self):
        self.owner, self.shop = make_owner_shop()
        self.client = api_client_for(self.owner)
        self.product = make_product(self.shop, name="Cola 33cl", quantity=2, sku="COLA")

    def test_product_suggestions(self):
        response = self.client.get("/api/v1/suggest/products/", {"q": "cola"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["results"])

    def test_suggestions_never_leak_another_shop(self):
        _o, other = make_owner_shop("autre", "Autre")
        make_product(other, name="Cola secret", quantity=1, sku="SEC")
        response = api_client_for(self.owner).get("/api/v1/suggest/products/", {"q": "cola"})
        labels = [row["label"] for row in response.data["results"]]
        self.assertNotIn("Cola secret", labels)