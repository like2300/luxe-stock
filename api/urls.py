"""Table des routes de l'API, toutes sous le préfixe `/api/v1/`.

Le préfixe est posé dans `stockpro/urls.py` : le web garde ses propres routes et
les noms de ses URL ne changent pas.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .sync import SyncPhotoView

router = DefaultRouter()
router.register("products", views.ProductViewSet, basename="product")
router.register("categories", views.CategoryViewSet, basename="category")
router.register("movements", views.MovementViewSet, basename="movement")

urlpatterns = [
    # ---------- Compte ----------
    path("auth/login/", views.LoginView.as_view(), name="api-auth-login"),
    path("auth/signup/", views.SignupView.as_view(), name="api-auth-signup"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api-auth-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="api-auth-logout"),

    # ---------- Boutique ----------
    path("shops/", views.ShopCreateView.as_view(), name="api-shop-create"),
    path("shops/current/", views.ShopCurrentView.as_view(), name="api-shop-current"),
    path(
        "shops/current/reset_theme/",
        views.ShopThemeResetView.as_view(),
        name="api-shop-reset-theme",
    ),

    # ---------- Tableau de bord ----------
    path("dashboard/", views.DashboardView.as_view(), name="api-dashboard"),

    # ---------- Produits, catégories, mouvements (routage automatique) ----------
    *router.urls,

    # ---------- Notifications ----------
    path(
        "notifications/",
        views.NotificationListView.as_view(),
        name="api-notification-list",
    ),
    path(
        "notifications/read_all/",
        views.NotificationReadAllView.as_view(),
        name="api-notification-read-all",
    ),
    path(
        "notifications/clear/",
        views.NotificationClearView.as_view(),
        name="api-notification-clear",
    ),
    path(
        "notifications/<uuid:uuid>/read/",
        views.NotificationReadView.as_view(),
        name="api-notification-read",
    ),

    # ---------- Employés ----------
    path("employees/", views.EmployeeListCreateView.as_view(), name="api-employee-list"),
    path(
        "employees/<uuid:uuid>/",
        views.EmployeeDetailView.as_view(),
        name="api-employee-detail",
    ),

    # ---------- Profil ----------
    path("profile/", views.ProfileView.as_view(), name="api-profile"),
    path(
        "profile/photo/",
        views.ProfilePhotoDeleteView.as_view(),
        name="api-profile-photo",
    ),

    # ---------- Scanner ----------
    path("scan/config/", views.ScanConfigView.as_view(), name="api-scan-config"),
    path("scan/", views.ScanLookupView.as_view(), name="api-scan"),
    path("scan/movements/", views.ScanMovementBatchView.as_view(), name="api-scan-movements"),

    # ---------- Suggestions ----------
    path("suggest/products/", views.SuggestProductsView.as_view(), name="api-suggest-products"),
    path(
        "suggest/categories/",
        views.SuggestCategoriesView.as_view(),
        name="api-suggest-categories",
    ),
    path("suggest/movements/", views.SuggestMovementsView.as_view(), name="api-suggest-movements"),
    path("suggest/employees/", views.SuggestEmployeesView.as_view(), name="api-suggest-employees"),
    path(
        "suggest/notifications/",
        views.SuggestNotificationsView.as_view(),
        name="api-suggest-notifications",
    ),

    # ---------- Synchronisation ----------
    path("sync/status/", views.SyncStatusView.as_view(), name="api-sync-status"),
    path("sync/pull/", views.SyncPullView.as_view(), name="api-sync-pull"),
    path("sync/push/", views.SyncPushView.as_view(), name="api-sync-push"),
    path("sync/push/photo/", SyncPhotoView.as_view(), name="api-sync-push-photo"),
    path("sync/operations/", views.SyncOperationsView.as_view(), name="api-sync-operations"),
]