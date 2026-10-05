from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="auth/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("inscription/", views.signup, name="signup"),
    path("boutique/creer/", views.create_shop, name="create_shop"),
    path("parametres/", views.shop_settings, name="settings"),
    path("produits/", views.product_list, name="product_list"),
    path("produits/ajouter/", views.product_create, name="product_create"),
    path("produits/<int:pk>/modifier/", views.product_edit, name="product_edit"),
    path("produits/<int:pk>/supprimer/", views.product_delete, name="product_delete"),
    path("categories/", views.category_list, name="category_list"),
    path(
        "categories/<int:pk>/supprimer/", views.category_delete, name="category_delete"
    ),
    path("mouvements/", views.movement_list, name="movement_list"),
    path("mouvements/nouveau/", views.movement_create, name="movement_create"),
    path("scanner/", views.scan, name="scan"),
    path("api/scan/", views.scan_api, name="scan_api"),
    path("api/scan/mouvement/", views.scan_movement_api, name="scan_movement_api"),
    path("api/produits/suggestions/", views.product_suggest, name="product_suggest"),
    path(
        "api/categories/suggestions/", views.category_suggest, name="category_suggest"
    ),
    path("mouvements/recherche/", views.search_movements, name="search_movements"),
    path("api/suggestions/produits/", views.suggest_products, name="suggest_products"),
    path("api/suggestions/categories/", views.suggest_categories, name="suggest_categories"),
    path("api/suggestions/mouvements/", views.suggest_movements, name="suggest_movements"),
    path("api/suggestions/employes/", views.suggest_employees, name="suggest_employees"),
    path("api/suggestions/notifications/", views.suggest_notifications, name="suggest_notifications"),
    path("notifications/", views.notification_list, name="notification_list"),
    path(
        "notifications/<int:pk>/lue/", views.notification_read, name="notification_read"
    ),
    path(
        "notifications/tout/lire/",
        views.notification_read_all,
        name="notification_read_all",
    ),
    path("notifications/vider/", views.notification_clear, name="notification_clear"),
    path("employes/", views.employee_list, name="employee_list"),
    path("employes/ajouter/", views.employee_create, name="employee_create"),
    path("employes/<int:pk>/modifier/", views.employee_edit, name="employee_edit"),
    path("employes/<int:pk>/supprimer/", views.employee_delete, name="employee_delete"),
    # API du profil connecte (avatar, initiales, informations)
    path("api/profil/", views.profile_api, name="profile_api"),
    path("api/profil/modifier/", views.profile_api_update, name="profile_api_update"),
    path(
        "api/profil/photo/supprimer/",
        views.profile_photo_delete,
        name="profile_photo_delete",
    ),
]
