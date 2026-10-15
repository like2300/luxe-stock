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
    path("categories/<int:pk>/modifier/", views.category_edit, name="category_edit"),
    path(
        "categories/<int:pk>/supprimer/", views.category_delete, name="category_delete"
    ),
    path("mouvements/", views.movement_list, name="movement_list"),
    path("mouvements/nouveau/", views.movement_create, name="movement_create"),
    path("mouvements/<int:pk>/modifier/", views.movement_edit, name="movement_edit"),
    path("mouvements/<int:pk>/supprimer/", views.movement_delete, name="movement_delete"),
    path("mouvements/<int:pk>/ticket/", views.movement_ticket, name="movement_ticket"),
    path("mouvements/<int:pk>/livraison/", views.movement_delivery, name="movement_delivery"),
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
    # Finance (propriétaire)
    path("finance/", views.finance, name="finance"),
    path("finance/depenses/ajouter/", views.expense_create, name="expense_create"),
    path(
        "finance/depenses/<int:pk>/supprimer/",
        views.expense_delete,
        name="expense_delete",
    ),
    # Clients
    path("clients/", views.customer_list, name="customer_list"),
    path("clients/ajouter/", views.customer_create, name="customer_create"),
    path("clients/<int:pk>/modifier/", views.customer_edit, name="customer_edit"),
    path("clients/<int:pk>/supprimer/", views.customer_delete, name="customer_delete"),
    path("api/suggestions/clients/", views.suggest_customers, name="suggest_customers"),
    path("api/clients/<int:pk>/", views.customer_info_api, name="customer_info_api"),
    # Factures
    path("factures/", views.invoice_list, name="invoice_list"),
    path("factures/nouvelle/", views.invoice_create, name="invoice_create"),
    path("factures/<int:pk>/supprimer/", views.invoice_delete, name="invoice_delete"),
    path("factures/<int:pk>/ticket/", views.invoice_ticket, name="invoice_ticket"),
    # Livraisons
    path("livraisons/", views.delivery_list, name="delivery_list"),
    path("livraisons/nouvelle/", views.delivery_create, name="delivery_create"),
    path("livraisons/zones/", views.delivery_zones, name="delivery_zones"),
    path("livraisons/zones/<int:pk>/modifier/", views.delivery_zone_edit, name="delivery_zone_edit"),
    path(
        "livraisons/zones/<int:pk>/supprimer/",
        views.delivery_zone_delete,
        name="delivery_zone_delete",
    ),
    path("livraisons/<int:pk>/modifier/", views.delivery_edit, name="delivery_edit"),
    path(
        "livraisons/<int:pk>/statut/",
        views.delivery_set_status,
        name="delivery_set_status",
    ),
    path("livraisons/<int:pk>/supprimer/", views.delivery_delete, name="delivery_delete"),
    path("api/factures/<int:pk>/", views.invoice_info_api, name="invoice_info_api"),
]
