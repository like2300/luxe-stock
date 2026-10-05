import json
import shutil
import tempfile
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.models import SocialAccount
from PIL import Image

from .models import PERMISSIONS, Membership, Notification, Product, Profile, Shop, StockMovement


def image_upload(name="moi.png", fmt="PNG", color="red"):
    """Petit fichier image valide, pour tester l'envoi de la photo de profil."""
    import io

    buf = io.BytesIO()
    Image.new("RGB", (40, 40), color).save(buf, format=fmt)
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=f"image/{fmt.lower()}")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="tests-media-"))
class ProfileApiTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            "boss", password="Zx9!kqPw72", first_name="Jean", last_name="Dupont"
        )
        self.shop = Shop.objects.create(owner=self.user, name="Ma Boutique", currency="FCFA")
        Membership.objects.create(user=self.user, shop=self.shop, is_owner=True)
        self.client.login(username="boss", password="Zx9!kqPw72")

    def test_api_returns_profile_and_initials(self):
        r = self.client.get(reverse("profile_api"))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["full_name"], "Jean Dupont")
        self.assertEqual(data["role"], "Propriétaire")
        self.assertEqual(data["shop_name"], "Ma Boutique")
        self.assertEqual(len(data["permissions"]), len(PERMISSIONS))
        # Sans photo, l'interface affiche les initiales.
        self.assertIsNone(data["photo_url"])
        self.assertEqual(data["avatar"]["initials"], "JD")
        self.assertFalse(data["avatar"]["has_photo"])

    def test_page_shows_initials_and_profile_popup(self):
        r = self.client.get(reverse("product_list"))
        self.assertContains(r, "JD")
        self.assertContains(r, 'id="profile-modal"')
        self.assertContains(r, reverse("profile_api"))
        self.assertNotContains(r, "avatars.githubusercontent.com")

    def test_upload_photo_then_delete(self):
        r = self.client.post(
            reverse("profile_api_update"),
            {"photo": image_upload(), "phone": "06 12 34 56 78", "bio": "Gerant"},
        )
        self.assertEqual(r.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.photo)
        self.assertEqual(profile.phone, "06 12 34 56 78")
        self.assertEqual(profile.bio, "Gerant")

        data = r.json()
        self.assertTrue(data["has_uploaded_photo"])
        self.assertTrue(data["photo_url"].startswith("/media/profiles/"))
        self.assertContains(self.client.get(reverse("product_list")), data["photo_url"])

        # Un nouvel appel sans fichier ne doit pas effacer la photo.
        self.assertTrue(self.client.post(reverse("profile_api_update"), {}).json()["has_uploaded_photo"])

        r = self.client.post(reverse("profile_photo_delete"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["has_uploaded_photo"])
        self.assertFalse(Profile.objects.get(user=self.user).photo)

    def test_non_image_is_rejected(self):
        faux = SimpleUploadedFile("faux.png", b"ceci-n-est-pas-une-image" * 10, content_type="image/png")
        r = self.client.post(reverse("profile_api_update"), {"photo": faux})
        self.assertEqual(r.status_code, 400)
        self.assertIn("photo", r.json()["errors"])
        self.assertFalse(Profile.objects.get(user=self.user).photo)

    def test_photo_comes_from_oauth_provider_when_none_uploaded(self):
        SocialAccount.objects.create(
            user=self.user, provider="google", uid="1",
            extra_data={"picture": "https://lh3.googleusercontent.com/a/photo-test"},
        )
        data = self.client.get(reverse("profile_api")).json()
        self.assertEqual(data["photo_url"], "https://lh3.googleusercontent.com/a/photo-test")

    def test_api_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse("profile_api"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("login"), r["Location"])

    def test_employee_sees_own_profile_role(self):
        self.client.post(reverse("employee_create"),
                         {"username": "emp", "password": "Zx9!kqPw72", "can_view_products": "on"})
        self.client.logout()
        self.client.login(username="emp", password="Zx9!kqPw72")
        data = self.client.get(reverse("profile_api")).json()
        self.assertEqual(data["role"], "Employé")
        self.assertEqual(data["username"], "emp")
        self.assertEqual(data["avatar"]["initials"], "E")
        # Un employé ne doit pas voir les permissions du propriétaire.
        self.assertNotIn("Supprimer des produits", data["permissions"])


class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("boss", password="Zx9!kqPw72")
        self.shop = Shop.objects.create(owner=self.user, name="Ma Boutique", currency="FCFA")
        Membership.objects.create(user=self.user, shop=self.shop, is_owner=True)
        self.client.login(username="boss", password="Zx9!kqPw72")
        self.product_data = {
            "name": "Jus", "sku": "", "category": "", "cost_price": "300",
            "sale_price": "500", "alert_threshold": "3",
        }

    def add_product(self, quantity=42):
        self.client.post(reverse("product_create"), {**self.product_data, "quantity": quantity})
        return Product.objects.get()

    def test_product_added_creates_notification(self):
        self.add_product()
        n = Notification.objects.get()
        self.assertEqual(n.kind, Notification.PRODUCT_ADDED)
        self.assertEqual(n.sound_code, "AJOUT")
        self.assertEqual(n.quantity, 42)
        self.assertEqual(n.level, "ok")
        self.assertFalse(n.is_read)

    def test_quantity_is_editable_and_traced(self):
        p = self.add_product()
        data = {**self.product_data, "name": "Jus", "quantity": "999"}
        self.client.post(reverse("product_edit", args=[p.pk]), data)

        p.refresh_from_db()
        self.assertEqual(p.quantity, 999)
        # La correction doit rester justifiée par un mouvement.
        self.assertEqual(p.movements.count(), 2)
        ajustement = p.movements.exclude(note="Stock initial").get()
        self.assertEqual((ajustement.kind, ajustement.quantity), ("IN", 957))
        self.assertEqual(
            Notification.objects.filter(kind=Notification.ADJUSTED).count(), 1
        )

    def test_edit_without_quantity_change_creates_no_movement(self):
        p = self.add_product()
        self.client.post(reverse("product_edit", args=[p.pk]),
                         {**self.product_data, "quantity": "42"})
        self.assertEqual(p.movements.count(), 1)

    def test_negative_quantity_is_rejected(self):
        p = self.add_product()
        r = self.client.post(reverse("product_edit", args=[p.pk]),
                             {**self.product_data, "quantity": "-5"})
        self.assertContains(r, "négative")
        p.refresh_from_db()
        self.assertEqual(p.quantity, 42)

    def test_threshold_crossing_and_rupture_escalation(self):
        p = self.add_product()
        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "OUT", "quantity": "40", "note": "vente"})
        bas = Notification.objects.get(kind=Notification.LOW_STOCK)
        self.assertEqual(bas.sound_code, "BAS")
        self.assertEqual(bas.quantity, 2)
        self.assertEqual(bas.level, "bas")

        # Tant que le stock reste sous le seuil, aucune nouvelle alerte.
        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "OUT", "quantity": "1", "note": "vente"})
        self.assertEqual(Notification.objects.filter(kind=Notification.LOW_STOCK).count(), 1)

        # Passage à zéro : escalade vers la rupture.
        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "OUT", "quantity": "1", "note": "vente"})
        rupture = Notification.objects.get(kind=Notification.OUT_OF_STOCK)
        self.assertEqual(rupture.sound_code, "RUPTURE")
        self.assertEqual(rupture.level, "rupture")
        self.assertEqual(Notification.objects.filter(kind=Notification.OUT_OF_STOCK).count(), 1)

    def test_movement_notifications(self):
        p = self.add_product()
        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "OUT", "quantity": "5", "note": "vente"})
        self.assertTrue(Notification.objects.filter(
            kind=Notification.STOCK_OUT, sound_code="SORTIE").exists())

        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "IN", "quantity": "9", "note": "réception"})
        self.assertTrue(Notification.objects.filter(
            kind=Notification.STOCK_IN, sound_code="ENTREE").exists())

    def test_notification_page_renders_codes_and_colors(self):
        p = self.add_product()
        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "OUT", "quantity": "40", "note": "vente"})
        r = self.client.get(reverse("notification_list"))
        self.assertContains(r, "AJOUT")
        self.assertContains(r, "SORTIE")
        self.assertContains(r, "BAS")
        self.assertContains(r, "Stock bas")
        self.assertContains(r, "sounds.js")
        self.assertContains(r, "Non lues")

    def test_mark_read_and_clear(self):
        p = self.add_product()
        n = Notification.objects.first()
        self.client.post(reverse("notification_read", args=[n.pk]))
        n.refresh_from_db()
        self.assertTrue(n.is_read)

        self.client.post(reverse("movement_create"),
                         {"product": p.pk, "kind": "OUT", "quantity": "1", "note": "vente"})
        self.assertTrue(Notification.objects.filter(is_read=False).exists())
        self.client.post(reverse("notification_read_all"))
        self.assertFalse(Notification.objects.filter(is_read=False).exists())

        self.client.post(reverse("notification_clear"))
        self.assertEqual(Notification.objects.count(), 0)

    def test_notifications_are_isolated_per_shop(self):
        self.add_product()
        autre = User.objects.create_user("autre", password="Zx9!kqPw72")
        shop2 = Shop.objects.create(owner=autre, name="Autre", currency="EUR")
        Membership.objects.create(user=autre, shop=shop2, is_owner=True)
        Product.objects.create(shop=shop2, name="Secret", quantity=1)

        self.client.login(username="autre", password="Zx9!kqPw72")
        r = self.client.get(reverse("notification_list"))
        self.assertNotContains(r, "AJOUT")
        self.assertContains(r, "Aucune notification")

    def test_readonly_employee_cannot_see_notifications(self):
        p = self.add_product()
        self.client.post(reverse("employee_create"),
                         {"username": "emp", "password": "Zx9!kqPw72",
                          "can_view_products": "on"})
        self.client.logout()
        self.client.login(username="emp", password="Zx9!kqPw72")
        # Lecture seule : la page est visible, l'écriture sur la quantité non.
        self.assertEqual(self.client.get(reverse("notification_list")).status_code, 200)
        self.assertEqual(self.client.post(
            reverse("product_edit", args=[p.pk]),
            {**self.product_data, "quantity": "1"}).status_code, 403)


class ScanTests(TestCase):
    """Lecture de codes-barres : recherche, mouvements par lot et permissions."""

    PASSWORD = "Zx9!kqPw72"

    def setUp(self):
        self.user = User.objects.create_user("boss", password=self.PASSWORD)
        self.shop = Shop.objects.create(owner=self.user, name="Ma Boutique", currency="FCFA")
        Membership.objects.create(user=self.user, shop=self.shop, is_owner=True)
        self.client.login(username="boss", password=self.PASSWORD)
        self.product = Product.objects.create(
            shop=self.shop, name="Jus", sku="PRD-0001", barcode="6194000000015", quantity=10
        )

        # Autre boutique, pour vérifier qu'aucun produit ne fuite entre boutiques.
        self.other_user = User.objects.create_user("autre", password=self.PASSWORD)
        self.other_shop = Shop.objects.create(owner=self.other_user, name="Autre", currency="EUR")
        Membership.objects.create(user=self.other_user, shop=self.other_shop, is_owner=True)
        self.other_product = Product.objects.create(
            shop=self.other_shop, name="Secret", barcode="3012345678900", quantity=3
        )

    def add_employee(self, **perms):
        self.client.post(reverse("employee_create"), {
            "username": "emp", "password": self.PASSWORD, **perms})
        self.client.logout()
        self.client.login(username="emp", password=self.PASSWORD)

    def scan(self, code):
        return self.client.get(reverse("scan_api"), {"code": code}).json()

    def post_lines(self, items, kind="OUT", note=""):
        return self.client.post(
            reverse("scan_movement_api"),
            data=json.dumps({"items": items, "kind": kind, "note": note}),
            content_type="application/json",
        )

    # ---------- Recherche ----------
    def test_lookup_by_barcode(self):
        data = self.scan("6194000000015")
        self.assertTrue(data["found"])
        self.assertEqual(data["id"], self.product.pk)
        self.assertEqual(data["name"], "Jus")
        self.assertEqual(data["sku"], "PRD-0001")
        self.assertEqual(data["stock"], 10)
        self.assertEqual(data["level"], "ok")

    def test_lookup_by_sku(self):
        data = self.scan("PRD-0001")
        self.assertTrue(data["found"])
        self.assertEqual(data["id"], self.product.pk)

    def test_lookup_unknown_code(self):
        self.assertEqual(self.scan("0000000000000"), {"found": False, "code": "0000000000000"})

    def test_other_shop_code_is_not_returned(self):
        self.assertFalse(self.scan("3012345678900")["found"])

    def test_scan_page_requires_view_products(self):
        self.add_employee()  # aucune permission
        self.assertEqual(self.client.get(reverse("scan")).status_code, 403)
        self.assertEqual(self.client.get(reverse("scan_api"), {"code": "6194000000015"}).status_code, 403)

    def test_movements_require_manage_stock(self):
        self.add_employee(can_view_products="on")
        r = self.post_lines([{"product_id": self.product.pk, "quantity": 1}])
        self.assertEqual(r.status_code, 403)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)

    # ---------- Mouvements ----------
    def test_scan_out_records_movement_and_notification(self):
        r = self.post_lines([{"product_id": self.product.pk, "quantity": 3}], note="vente")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 7)
        m = self.product.movements.get()
        self.assertEqual((m.kind, m.quantity, m.note), ("OUT", 3, "vente"))
        self.assertTrue(Notification.objects.filter(
            product=self.product, kind=Notification.STOCK_OUT, sound_code="SORTIE").exists())

    def test_scan_in_records_movement(self):
        r = self.post_lines([{"product_id": self.product.pk, "quantity": 4}], kind="IN")
        self.assertEqual(r.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 14)
        self.assertEqual(self.product.movements.get().kind, "IN")

    def test_out_above_stock_is_refused(self):
        r = self.post_lines([{"product_id": self.product.pk, "quantity": 11}])
        self.assertEqual(r.status_code, 400)
        self.assertIn("stock insuffisant", r.json()["errors"][0].lower())
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.movements.count(), 0)

    def test_batch_is_atomic(self):
        # La 2e ligne est invalide : la 1re ne doit pas être enregistree.
        r = self.post_lines([
            {"product_id": self.product.pk, "quantity": 2},
            {"product_id": self.other_product.pk, "quantity": 1},
        ])
        self.assertEqual(r.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)

    def test_invalid_quantity_is_refused(self):
        for qty in (0, -3, "abc"):
            r = self.post_lines([{"product_id": self.product.pk, "quantity": qty}])
            self.assertEqual(r.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)

    def test_invalid_kind_and_empty_batch(self):
        self.assertEqual(
            self.post_lines([{"product_id": self.product.pk, "quantity": 1}], kind="XX").status_code, 400)
        self.assertEqual(self.post_lines([]).status_code, 400)

    # ---------- Unicité du code-barres ----------
    def test_barcode_unique_per_shop_but_empty_allowed(self):
        form_data = {
            "name": "Eau", "sku": "", "barcode": "", "category": "",
            "cost_price": "100", "sale_price": "150", "quantity": "1", "alert_threshold": "1",
        }
        self.assertEqual(self.client.post(reverse("product_create"), form_data).status_code, 302)
        self.assertEqual(self.client.post(reverse("product_create"), form_data).status_code, 302)
        self.assertEqual(Product.objects.filter(barcode="").count(), 2)

        # Deux produits sans code coexistent, le meme code est refuse une seule fois.
        self.assertEqual(
            self.client.post(reverse("product_create"), {**form_data, "barcode": "1234567890"}).status_code, 302)
        r = self.client.post(reverse("product_create"), {**form_data, "barcode": "1234567890"})
        self.assertContains(r, "déjà attribué à un autre produit")
        # Le meme code est autorise dans une autre boutique.
        self.client.login(username="autre", password=self.PASSWORD)
        self.assertEqual(
            self.client.post(reverse("product_create"), {**form_data, "barcode": "6194000000015"}).status_code, 302)

    def test_barcode_is_normalized_and_prefilled(self):
        r = self.client.post(reverse("product_create"), {
            "name": "Soda", "sku": "", "barcode": " 6194 0000 0015 ", "category": "",
            "cost_price": "100", "sale_price": "150", "quantity": "0", "alert_threshold": "1",
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Product.objects.get(name="Soda").barcode, "619400000015")

        r = self.client.get(reverse("product_create"), {"barcode": "3012345678900"})
        self.assertContains(r, 'value="3012345678900"')

    def test_scan_page_shows_create_button_only_with_permission(self):
        self.assertContains(self.client.get(reverse("scan")), "Créer ce produit")
        self.add_employee(can_view_products="on")
        body = self.client.get(reverse("scan")).content.decode()
        self.assertNotIn("Créer ce produit", body)
        self.assertNotIn(reverse("scan_movement_api"), body)

    # ---------- Activation / desactivation depuis les parametres ----------
    def disable_scanner(self):
        self.shop.scanner_enabled = False
        self.shop.save(update_fields=["scanner_enabled"])

    def test_settings_toggle_hides_the_scanner_everywhere(self):
        self.assertContains(self.client.get(reverse("product_list")), ">Scanner<")
        self.assertContains(self.client.get(reverse("dashboard")), reverse("scan"))

        self.disable_scanner()
        self.assertNotContains(self.client.get(reverse("product_list")), ">Scanner<")
        self.assertNotContains(self.client.get(reverse("dashboard")), reverse("scan"))
        self.assertNotContains(self.client.get(reverse("product_create")), 'id="barcode-scan-btn"')

    def test_disabled_scanner_refuses_page_and_api(self):
        self.disable_scanner()
        self.assertEqual(self.client.get(reverse("scan")).status_code, 403)
        self.assertEqual(
            self.client.get(reverse("scan_api"), {"code": "6194000000015"}).status_code, 403)
        r = self.post_lines([{"product_id": self.product.pk, "quantity": 1}])
        self.assertEqual(r.status_code, 403)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)

    def test_settings_form_saves_the_toggle(self):
        r = self.client.post(reverse("settings"), {
            "name": "Ma Boutique", "currency": "FCFA", "address": "", "phone": "",
            "primary_color": "#5bc0de", "sidebar_color": "#3d4b5c",
            "header_color": "#4a5868", "background_color": "#e9edf4",
        })
        self.assertEqual(r.status_code, 302)
        self.shop.refresh_from_db()
        self.assertFalse(self.shop.scanner_enabled)

        # Case cochee : le scanner redevient disponible.
        self.client.post(reverse("settings"), {
            "name": "Ma Boutique", "currency": "FCFA", "address": "", "phone": "",
            "primary_color": "#5bc0de", "sidebar_color": "#3d4b5c",
            "header_color": "#4a5868", "background_color": "#e9edf4",
            "scanner_enabled": "1",
        })
        self.shop.refresh_from_db()
        self.assertTrue(self.shop.scanner_enabled)
        self.assertEqual(self.client.get(reverse("scan")).status_code, 200)


class FlowTests(TestCase):
    def test_full_flow(self):
        c = self.client
        r = c.post(reverse("signup"), {"username": "boss", "password1": "Zx9!kqPw72", "password2": "Zx9!kqPw72"})
        self.assertRedirects(r, reverse("create_shop"))
        r = c.post(reverse("create_shop"), {"name": "Ma Boutique", "currency": "FCFA"})
        self.assertRedirects(r, reverse("dashboard"))
        shop = Shop.objects.get()
        self.assertTrue(Membership.objects.get(user__username="boss").is_owner)

        c.post(reverse("category_list"), {"name": "Boissons"})
        r = c.post(reverse("product_create"), {"name": "Jus", "sku": "", "category": shop.categories.get().pk,
                                              "cost_price": "300", "sale_price": "500", "quantity": "10", "alert_threshold": "3"})
        self.assertRedirects(r, reverse("product_list"))
        p = Product.objects.get()
        self.assertEqual(p.sku, "PRD-0001")
        self.assertEqual(p.movements.count(), 1)

        c.post(reverse("movement_create"), {"product": p.pk, "kind": "OUT", "quantity": "4", "note": "vente"})
        p.refresh_from_db(); self.assertEqual(p.quantity, 6)
        r = c.post(reverse("movement_create"), {"product": p.pk, "kind": "OUT", "quantity": "99"})
        self.assertContains(r, "Stock insuffisant")

        # thème
        c.post(reverse("settings"), {"name": "Ma Boutique", "currency": "FCFA", "primary_color": "#ff0000",
                                     "sidebar_color": "#111111", "header_color": "#222222", "background_color": "#eeeeee"})
        self.assertContains(c.get(reverse("dashboard")), "--primary:#ff0000")
        r = c.post(reverse("settings"), {"name": "x", "currency": "F", "primary_color": "red;}</style>",
                                         "sidebar_color": "#111111", "header_color": "#222222", "background_color": "#eeeeee"})
        self.assertContains(r, "class=\"err\"")
        shop.refresh_from_db(); self.assertEqual(shop.primary_color, "#ff0000"); self.assertEqual(shop.name, "Ma Boutique")

        # employé : lecture seule
        c.post(reverse("employee_create"), {"username": "emp", "password": "Zx9!kqPw72", "can_view_products": "on"})
        c.logout()
        self.assertTrue(c.login(username="emp", password="Zx9!kqPw72"))
        self.assertEqual(c.get(reverse("product_list")).status_code, 200)
        self.assertEqual(c.get(reverse("product_create")).status_code, 403)
        self.assertEqual(c.get(reverse("settings")).status_code, 403)
        self.assertEqual(c.get(reverse("employee_list")).status_code, 403)
        self.assertEqual(c.post(reverse("product_delete", args=[p.pk])).status_code, 403)
        self.assertContains(c.get(reverse("dashboard")), "--primary:#ff0000")

    def test_isolation(self):
        for u in ("a", "b"):
            self.client.post(reverse("signup"), {"username": u, "password1": "Zx9!kqPw72", "password2": "Zx9!kqPw72"})
            self.client.post(reverse("create_shop"), {"name": f"S{u}", "currency": "F"})
            self.client.post(reverse("product_create"), {"name": f"P{u}", "cost_price": "1", "sale_price": "2", "quantity": "1", "alert_threshold": "1"})
            self.client.logout()
        pa = Product.objects.get(name="Pa")
        self.client.login(username="b", password="Zx9!kqPw72")
        self.assertEqual(self.client.get(reverse("product_edit", args=[pa.pk])).status_code, 404)


GOOGLE_USERINFO = {
    "id": "110000000000000000001",
    "email": "client@example.com",
    "verified_email": True,
    "given_name": "Jean",
    "family_name": "Dupont",
}

#allauth fusionne les apps issues de la base et celles des settings : on ne crée
# donc pas de SocialApp en base, et on fige des identifiants factices pour que les
# tests ne dépendent pas du fichier .env.
GOOGLE_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online", "prompt": "select_account"},
        "APP": {
            "client_id": "test-client-id.apps.googleusercontent.com",
            "secret": "test-client-secret",
            "key": "",
        },
    }
}


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {"content-type": "application/json"}
        self.text = "{}"
        self.content = b"{}"

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return self._payload


class _FakeSession:
    """Remplace la session HTTP d'allauth : aucune requête ne sort réellement."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def close(self):
        pass

    def request(self, method, url, **kwargs):
        if url.endswith("/token"):
            return _FakeResponse({"access_token": "fake-token", "token_type": "Bearer"})
        return _FakeResponse(GOOGLE_USERINFO)

    def get(self, url, **kwargs):
        return _FakeResponse(GOOGLE_USERINFO)


@override_settings(SOCIALACCOUNT_PROVIDERS=GOOGLE_PROVIDERS,
                   ACCOUNT_DEFAULT_HTTP_PROTOCOL="http")
class GoogleOAuthTests(TestCase):
    def _patched(self):
        return patch(
            "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_requests_session",
            return_value=_FakeSession(),
        )

    def _begin_google_flow(self):
        r = self.client.get(reverse("google_login"))
        self.assertEqual(r.status_code, 302)
        return r["Location"]

    def test_button_rendered_on_login_and_signup(self):
        for url, label in ((reverse("login"), "Se connecter avec Google"),
                           (reverse("signup"), "S'inscrire avec Google")):
            r = self.client.get(url)
            self.assertContains(r, label)
            self.assertContains(r, "g-btn")
            self.assertContains(r, "/accounts/google/login/")

    def test_button_hidden_when_not_configured(self):
        with override_settings(SOCIALACCOUNT_PROVIDERS={
            "google": {"APP": {"client_id": "", "secret": ""}}
        }):
            self.assertNotContains(self.client.get(reverse("login")), "g-btn")

    def test_login_redirects_to_google_account_selector(self):
        target = self._begin_google_flow()
        self.assertTrue(target.startswith("https://accounts.google.com/o/oauth2/v2/auth"), target)
        self.assertIn("prompt=select_account", target)
        self.assertIn("access_type=online", target)
        # Le redirect_uri doit correspondre à celui déclaré dans la console Google.
        self.assertIn(
            urlencode({"redirect_uri": "http://testserver/accounts/google/login/callback/"}),
            target,
        )

    def test_callback_creates_account_then_shop(self):
        target = self._begin_google_flow()
        state = target.split("state=")[1].split("&")[0]

        with self._patched():
            r = self.client.get(reverse("google_callback"),
                               {"code": "auth-code", "state": state})

        user = User.objects.get(email="client@example.com")
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Dupont")
        self.assertTrue(SocialAccount.objects.filter(user=user, provider="google").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

        # Aucune boutique encore : le tableau de bord redirige vers la création.
        self.assertEqual(r["Location"], "/")
        self.assertRedirects(self.client.get("/"), reverse("create_shop"))

        r = self.client.post(reverse("create_shop"),
                             {"name": "Boutique Google", "currency": "FCFA"})
        self.assertRedirects(r, reverse("dashboard"))
        self.assertTrue(Membership.objects.get(user=user).is_owner)

    def test_second_login_reuses_existing_account(self):
        for _ in range(2):
            state = self._begin_google_flow().split("state=")[1].split("&")[0]
            with self._patched():
                self.client.get(reverse("google_callback"),
                                {"code": "auth-code", "state": state})
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(SocialAccount.objects.count(), 1)
