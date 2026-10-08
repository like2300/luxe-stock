"""Authentification : connexion, inscription, rafraichissement, deconnexion."""

from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Membership, Shop

from .factories import PASSWORD, anon_client, api_client_for, make_user


class LoginTests(TestCase):
    def setUp(self):
        self.client = anon_client()
        self.user = make_user("alice")

    def test_login_returns_access_and_refresh(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "alice", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_without_shop_still_succeeds(self):
        """Un compte sans boutique est connecte : il cree sa boutique ensuite."""
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "alice", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["user"]["shop_uuid"])

    def test_login_reports_shop_and_role(self):
        shop = Shop.objects.create(owner=self.user, name="Ma Boutique")
        Membership.objects.create(user=self.user, shop=shop, is_owner=True)
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "alice", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(response.data["user"]["shop_name"], "Ma Boutique")
        self.assertEqual(response.data["user"]["role"], "Propriétaire")

    def test_wrong_password_and_unknown_user_share_one_message(self):
        """Message unique : ne pas reveler quels comptes existent."""
        for username, password in (
            ("alice", "mauvais-mot-de-passe"),
            ("inconnu", PASSWORD),
        ):
            with self.subTest(username=username):
                response = self.client.post(
                    "/api/v1/auth/login/",
                    {"username": username, "password": password},
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
                messages = str(response.data)
                self.assertIn("corrects", messages)

    def test_inactive_account_is_refused(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "alice", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class RefreshTests(TestCase):
    def setUp(self):
        self.client = anon_client()
        self.user = make_user("alice")

    def test_refresh_returns_a_new_access_token(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(
            "/api/v1/auth/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_refresh_rejects_a_forged_token(self):
        response = self.client.post(
            "/api/v1/auth/refresh/", {"refresh": "pas-un-jwt"}, format="json"
        )
        self.assertEqual(response.status_code, 401)


class LogoutTests(TestCase):
    def setUp(self):
        self.user = make_user("alice")
        self.client = api_client_for(self.user)

    def test_logout_blacklists_the_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            "/api/v1/auth/logout/", {"refresh": str(refresh)}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        again = anon_client().post(
            "/api/v1/auth/refresh/", {"refresh": str(refresh)}, format="json"
        )
        self.assertEqual(again.status_code, 401)

    def test_logout_without_refresh_token_is_refused(self):
        response = self.client.post("/api/v1/auth/logout/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_logout_requires_authentication(self):
        response = anon_client().post("/api/v1/auth/logout/", {}, format="json")
        self.assertEqual(response.status_code, 401)