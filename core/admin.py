from decimal import Decimal

from django.contrib import admin
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest
from django.utils.html import format_html

from unfold.decorators import display

from .models import (PERMISSIONS, Category, Membership, Notification, Product, Shop,
                    StockMovement)


def badge(text, background, foreground):
    """Pastille colorée. Styles en ligne : le CSS d'Unfold est compilé par Tailwind
    puis purgé, les classes utilitaires souhaitées peuvent donc ne pas exister."""
    return format_html(
        '<span style="display:inline-block;padding:2px 9px;border-radius:10px;'
        "font-size:11px;font-weight:600;line-height:18px;background:{};color:{};"
        'white-space:nowrap;">{}</span>',
        background,
        foreground,
        text,
    )


def granted_permissions(membership):
    if membership.is_owner:
        return badge("Propriétaire", "#4c1d95", "#ede9fe")
    granted = [label for field, label in PERMISSIONS if getattr(membership, field)]
    if not granted:
        return badge("Lecture seule", "#e5e7eb", "#4b5563")
    return ", ".join(granted)


def annotate_shop_totals(queryset):
    """Ajoute products_count, members_count et stock_value à une queryset de Shop."""
    return queryset.annotate(
        products_count=Count("products", distinct=True),
        members_count=Count("members", distinct=True),
        stock_value=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("products__quantity") * F("products__cost_price"),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                )
            ),
            Value(Decimal("0")),
        ),
    )


class StockStatusFilter(admin.SimpleListFilter):
    title = "niveau de stock"
    parameter_name = "stock_level"

    def lookups(self, request, model_admin):
        return ("rupture", "Rupture"), ("bas", "Stock bas"), ("ok", "En stock")

    def queryset(self, request, queryset):
        if self.value() == "rupture":
            return queryset.filter(quantity__lte=0)
        if self.value() == "bas":
            return queryset.filter(quantity__gt=0, quantity__lte=F("alert_threshold"))
        if self.value() == "ok":
            return queryset.filter(quantity__gt=F("alert_threshold"))
        return queryset


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fields = ("user", "is_owner", "can_view_products", "can_add_products",
              "can_edit_products", "can_delete_products", "can_manage_stock",
              "can_manage_categories")
    autocomplete_fields = ("user",)


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    # « shop » est la FK vers le parent : on l'omet de fields au lieu de l'exclure.
    fields = ("name",)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "currency", "product_total", "member_total", "swatch")
    list_display_links = ("name",)
    list_filter = ("currency",)
    search_fields = ("name", "owner__username", "owner__email", "currency")
    readonly_fields = ("shop_summary",)
    ordering = ("name",)
    list_per_page = 25
    inlines = (MembershipInline, CategoryInline)

    fieldsets = (
        ("Informations", {
            "classes": ("tab",),
            "fields": ("name", "owner", "address", "phone", "currency"),
        }),
        ("Apparence", {
            "classes": ("tab",),
            "fields": ("logo", "primary_color", "sidebar_color", "header_color",
                       "background_color"),
            "description": "Couleurs au format #rrggbb. Elles pilotent le thème du site public.",
        }),
        ("Statistiques", {
            "classes": ("tab",),
            "fields": ("shop_summary",),
        }),
    )

    @display(description="Produits", ordering="products_count")
    def product_total(self, obj):
        return obj.products_count

    @display(description="Membres", ordering="members_count")
    def member_total(self, obj):
        return obj.members_count

    @display(description="Couleurs")
    def swatch(self, obj):
        return " ".join(
            format_html(
                '<span style="display:inline-block;width:13px;height:13px;border-radius:3px;'
                'border:1px solid #d5dbe3;background:{};" title="{}"></span>',
                color, color,
            )
            for color in (obj.primary_color, obj.sidebar_color, obj.header_color,
                          obj.background_color)
        )

    @display(description="Vue d'ensemble")
    def shop_summary(self, obj):
        return format_html(
            "<b>{}</b> produit(s) · <b>{}</b> membre(s) · valeur du stock au prix d'achat : "
            "<b>{}</b>", obj.products_count, obj.members_count, obj.stock_value,
        )

    def get_queryset(self, request: HttpRequest):
        return annotate_shop_totals(super().get_queryset(request))


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "shop", "role", "permissions", "can_view_products",
                    "can_add_products", "can_edit_products", "can_delete_products",
                    "can_manage_stock", "can_manage_categories")
    list_filter = ("is_owner", "shop", "can_view_products", "can_add_products",
                   "can_edit_products", "can_delete_products", "can_manage_stock",
                   "can_manage_categories")
    search_fields = ("user__username", "user__email", "user__first_name",
                     "user__last_name", "shop__name")
    autocomplete_fields = ("user", "shop")
    list_per_page = 30
    ordering = ("shop__name", "user__username")

    @display(description="Rôle")
    def role(self, obj):
        if obj.is_owner:
            return badge("Propriétaire", "#4c1d95", "#ede9fe")
        return badge("Employé", "#e9edf4", "#3c4858")

    @display(description="Droits effectifs")
    def permissions(self, obj):
        return granted_permissions(obj)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "shop", "product_total")
    list_display_links = ("name",)
    list_filter = ("shop",)
    search_fields = ("name", "shop__name")
    autocomplete_fields = ("shop",)
    ordering = ("shop__name", "name")
    list_per_page = 30

    @display(description="Produits", ordering="products_count")
    def product_total(self, obj):
        return obj.products_count

    def get_queryset(self, request: HttpRequest):
        # La relation inverse de Product.category s'appelle « product ».
        return super().get_queryset(request).annotate(products_count=Count("product"))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "shop", "sale_price", "quantity",
                    "level", "created_at")
    list_display_links = ("name",)
    list_filter = ("shop", "category", StockStatusFilter)
    search_fields = ("name", "sku", "description", "category__name", "shop__name")
    autocomplete_fields = ("shop", "category")
    readonly_fields = ("quantity", "created_at")
    date_hierarchy = "created_at"
    list_per_page = 30
    ordering = ("-created_at",)

    fieldsets = (
        ("Produit", {
            "classes": ("tab",),
            "fields": ("name", "sku", "category", "description"),
        }),
        ("Tarification et stock", {
            "classes": ("tab",),
            "fields": (("cost_price", "sale_price"), ("alert_threshold", "quantity"),
                       "created_at"),
            "description": "La quantité en stock n'est modifiable que via un mouvement "
                           "(entrée / sortie), afin de conserver un historique fiable.",
        }),
    )

    @display(description="Niveau", ordering="quantity")
    def level(self, obj):
        if obj.quantity <= 0:
            return badge("Rupture", "#fadbd8", "#b03a2e")
        if obj.is_low:
            return badge("Stock bas", "#fdecd2", "#b8730f")
        return badge("En stock", "#e3f4d6", "#4c8a1f")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "shop", "kind", "message", "quantity", "level",
                    "sound_code", "is_read", "user")
    list_filter = ("is_read", "kind", "level", "created_at", "shop")
    search_fields = ("message", "label", "sound_code", "product__name", "user__username")
    autocomplete_fields = ("shop", "product")
    readonly_fields = ("created_at", "shop", "product", "kind", "label", "message",
                       "quantity", "alert_threshold", "sound_code", "level", "user")
    date_hierarchy = "created_at"
    list_per_page = 40
    ordering = ("-created_at", "-id")

    def has_add_permission(self, request: HttpRequest):
        return False

    def has_change_permission(self, request: HttpRequest, obj=None):
        return False

    @display(description="Boutique", ordering="shop__name")
    def shop(self, obj):
        return obj.shop.name

    @display(description="Niveau", ordering="level")
    def level(self, obj):
        background, foreground = obj.colors
        return badge(obj.level, background, foreground)

    actions = ["mark_read"]

    @admin.action(description="Marquer les notifications sélectionnées comme lues")
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marquée(s) comme lue(s).")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "product", "shop", "kind", "signed", "note", "user")
    list_filter = ("kind", "created_at", "product__shop")
    search_fields = ("product__name", "product__sku", "note", "user__username")
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "product", "kind", "quantity", "note", "user")
    date_hierarchy = "created_at"
    list_per_page = 40
    ordering = ("-created_at", "-id")

    def has_add_permission(self, request: HttpRequest):
        return False

    def has_change_permission(self, request: HttpRequest, obj=None):
        return False

    @display(description="Boutique", ordering="product__shop__name")
    def shop(self, obj):
        return obj.product.shop.name

    @display(description="Type", ordering="kind")
    def kind(self, obj):
        if obj.kind == StockMovement.IN:
            return badge("Entrée", "#e3f4d6", "#4c8a1f")
        return badge("Sortie", "#fdecd2", "#b8730f")

    @display(description="Quantité", ordering="quantity")
    def signed(self, obj):
        return ("+" if obj.kind == StockMovement.IN else "−") + str(obj.quantity)
