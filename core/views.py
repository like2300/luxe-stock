import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .avatar import avatar_data, ensure_profile, get_profile
from .decorators import owner_required, perm_required, scanner_required, shop_required
from .forms import (
    CategoryForm,
    EmployeeForm,
    MovementForm,
    ProductForm,
    ProfileForm,
    ShopCreateForm,
    ShopSettingsForm,
    SignupForm,
)
from .models import (
    PERMISSIONS,
    Category,
    Membership,
    Notification,
    Product,
    Shop,
    StockMovement,
    push_notification,
    record_adjustment,
    record_movement,
)

# Nombre de notifications envoyées au gabarit : le filtrage et la pagination
# se font ensuite dans le navigateur, sans rechargement de page.
NOTIFICATION_FEED_LIMIT = 200


# ---------- Compte & boutique ----------
def redirect_next(request, fallback):
    """Redirige vers la page demandée, en refusant toute URL externe (open redirect)."""
    target = request.POST.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(target)
    return redirect(fallback)


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        # Deux backends sont configurés (ModelBackend + allauth) : sans cet argument
        # Django lève « You have multiple authentication backends configured ».
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("create_shop")
    return render(request, "auth/signup.html", {"form": form})


@login_required
def create_shop(request):
    if Membership.objects.filter(user=request.user).exists():
        return redirect("dashboard")
    form = ShopCreateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            Membership.objects.create(user=request.user, shop=shop, is_owner=True)
        messages.success(
            request, "Votre boutique est prête. Ajoutez vos premiers produits !"
        )
        return redirect("dashboard")
    return render(request, "auth/create_shop.html", {"form": form})


@owner_required
def shop_settings(request):
    shop = request.shop
    if request.method == "POST" and "reset" in request.POST:
        for f in ["primary_color", "sidebar_color", "header_color", "background_color"]:
            setattr(shop, f, Shop._meta.get_field(f).default)
        shop.save()
        messages.success(request, "Thème réinitialisé.")
        return redirect("settings")
    
    # Assurez-vous que shop existe bien
    try:
        shop_instance = Shop.objects.get(pk=shop.pk)
    except Shop.DoesNotExist:
        shop_instance = None
    
    form = ShopSettingsForm(
        request.POST or None,
        request.FILES or None,
        instance=shop_instance if shop_instance else None,
    )
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Paramètres enregistrés.")
        return redirect("settings")
    
    return render(request, "settings.html", {"form": form, "shop": shop})


# ---------- Tableau de bord ----------
MONTHS_FR = [
    "", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Août", "Sep", "Oct", "Nov", "Déc",
]


def stock_history(shop, months=6):
    """Series mensuelles reelles : entrees, sorties et evolution du stock."""
    first = timezone.now().date().replace(day=1)

    periods = []
    year, month = first.year, first.month
    for _ in range(months):
        periods.append((year, month))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    periods.reverse()
    starts = [timezone.datetime(year, month, 1) for year, month in periods]
    end = (starts[-1] + timezone.timedelta(days=32)).replace(day=1)

    movements = StockMovement.objects.filter(
        product__shop=shop, created_at__gte=starts[0], created_at__lt=end
    )
    per_month = {
        row["month"].date(): row
        for row in movements.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            entries=Sum("quantity", filter=Q(kind=StockMovement.IN)),
            exits=Sum("quantity", filter=Q(kind=StockMovement.OUT)),
        )
    }

    # Stock reporte du mois : tout ce qui a bouge avant la fenetre.
    stock = 0
    for row in (
        StockMovement.objects.filter(product__shop=shop, created_at__lt=starts[0])
        .values("kind")
        .annotate(total=Sum("quantity"))
    ):
        stock += row["total"] if row["kind"] == StockMovement.IN else -row["total"]

    labels, entries, exits, total = [], [], [], []
    for (year, month), start in zip(periods, starts):
        row = per_month.get(start.date(), {})
        ent = row.get("entries") or 0
        exi = row.get("exits") or 0
        stock += ent - exi
        labels.append(f"{MONTHS_FR[month]} {year}")
        entries.append(ent)
        exits.append(exi)
        total.append(stock)
    return {"labels": labels, "entries": entries, "exits": exits, "total": total}


@shop_required
def dashboard(request):
    shop = request.shop
    ctx = {"can_see": request.membership.has("can_view_products")}
    if ctx["can_see"]:
        products = shop.products.all()
        value = (
            products.aggregate(
                v=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("cost_price"),
                        output_field=DecimalField(max_digits=18, decimal_places=2),
                    )
                )
            )["v"]
            or 0
        )
        ctx.update(
            n_products=products.count(),
            n_categories=shop.categories.count(),
            n_low=products.filter(quantity__lte=F("alert_threshold")).count(),
            value=value,
            low_products=products.filter(quantity__lte=F("alert_threshold")).order_by(
                "quantity"
            )[:8],
            recent=StockMovement.objects.filter(product__shop=shop).select_related(
                "product", "user"
            )[:8],
            chart=stock_history(shop),
        )
    return render(request, "dashboard.html", ctx)


# ---------- Produits ----------
@perm_required("can_view_products")
def product_list(request):
    shop = request.shop
    if request.method == "POST":
        if request.POST.get("action") == "delete_selected":
            if not request.membership.has("can_delete_products"):
                return render(request, "403.html", status=403)
            ids = request.POST.getlist("ids")
            to_delete = shop.products.filter(pk__in=ids)
            count = to_delete.count()
            to_delete.delete()
            if count:
                messages.success(request, f"{count} produit(s) supprimé(s).")
            else:
                messages.error(request, "Aucun produit sélectionné.")
        return redirect("product_list")

    qs = shop.products.select_related("category")
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "").strip()
    if q:
        # Recherche sur le nom, la référence ET le nom de la catégorie.
        qs = qs.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(category__name__icontains=q)
        )
    if cat:
        # Le filtre accepte l'identique (signet ancien) ou le nom saisi/suggéré.
        if cat.isdigit():
            qs = qs.filter(category_id=cat)
        else:
            qs = qs.filter(category__name__iexact=cat)
    if request.GET.get("low"):
        qs = qs.filter(quantity__lte=F("alert_threshold"))
    try:
        per = int(request.GET.get("per", 10))
    except ValueError:
        per = 10
    per = per if per in (10, 25, 50, 100) else 10
    page = Paginator(qs, per).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    # Valeur affichée dans le champ « catégorie » : un ancien signet avec l'id
    # est retraduit en nom pour rester cohérent avec les suggestions.
    cat_label = cat
    if cat.isdigit():
        existing = shop.categories.filter(pk=cat).first()
        cat_label = existing.name if existing else ""
    return render(
        request,
        "product_list.html",
        {
            "page": page,
            "q": q,
            "cat": cat,
            "cat_label": cat_label,
            "per": per,
"low": bool(request.GET.get("low")),
            "categories": shop.categories.all(),
            "qs": params.urlencode(),
        },
    )


@perm_required("can_add_products")
def product_create(request):
    # Le scanner renvoie vers ?barcode=CODE : le code lu est pré-rempli.
    initial = {}
    barcode = request.GET.get("barcode", "").strip()
    if barcode:
        initial["barcode"] = barcode[:64]
    form = ProductForm(request.POST or None, shop=request.shop, initial=initial)
    categories = Category.objects.filter(shop=request.shop).order_by("name")
    
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        p.shop = request.shop
        p.save()
        if p.quantity > 0:
            StockMovement.objects.create(
                product=p, kind="IN", quantity=p.quantity, note="Stock initial", user=request.user
            )
        push_notification(p, Notification.PRODUCT_ADDED, user=request.user)
        messages.success(request, f"Produit « {p.name} » ajouté.")
        return redirect("product_list")
    
    return render(
        request,
        "product_create.html",
        {
            "form": form,
            "categories": categories,
            "title": "Ajouter un Produit",
            "crumb": "Produits",
        },
    )


@perm_required("can_edit_products")
def product_edit(request, pk):
    p = get_object_or_404(Product, pk=pk, shop=request.shop)
    # La quantité précédente doit être lue AVANT le is_valid() ci-dessous :
    # ModelForm._post_clean() recopie les données validées sur l'instance, donc
    # p.quantity vaut déjà la nouvelle valeur si on relit l'attribut après coup.
    before = p.quantity
    form = ProductForm(request.POST or None, instance=p, shop=request.shop)
    if request.method == "POST" and form.is_valid():
        form.save()
        p.refresh_from_db()
        if p.quantity != before:
            record_adjustment(p, before, request.user)
        messages.success(request, "Produit modifié.")
        return redirect("product_list")
    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "title": f"Modifier : {p.name}",
            "back": "product_list",
            "crumb": "Produits",
        },
    )


@require_POST
@perm_required("can_delete_products")
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk, shop=request.shop).delete()
    messages.success(request, "Produit supprimé.")
    return redirect("product_list")


# ---------- Catégories ----------
@perm_required("can_manage_categories")
def category_list(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save(commit=False)
        c.shop = request.shop
        if Category.objects.filter(shop=request.shop, name__iexact=c.name).exists():
            messages.error(request, "Cette catégorie existe déjà.")
        else:
            c.save()
            messages.success(request, "Catégorie ajoutée.")
        return redirect("category_list")
    return render(
        request,
        "category_list.html",
        {
            "form": form,
            "categories": request.shop.categories.filter(
                name__icontains=request.GET.get("q", "").strip()
            )
            if request.GET.get("q", "").strip()
            else request.shop.categories.all(),
            "q": request.GET.get("q", "").strip(),
        },
    )


@require_POST
@perm_required("can_manage_categories")
def category_delete(request, pk):
    get_object_or_404(Category, pk=pk, shop=request.shop).delete()
    messages.success(request, "Catégorie supprimée.")
    return redirect("category_list")


@perm_required("can_manage_stock")
def product_suggest(request):
    """Suggestions de produits pour l'autocompletion du formulaire de mouvement."""
    query = request.GET.get("q", "").strip()[:60]
    products = request.shop.products.select_related("category")
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(category__name__icontains=query)
        )
    products = products.order_by("name")[:12]
    return JsonResponse(
        {
            "results": [
                {
                    "id": p.pk,
                    "name": p.name,
                    "sku": p.sku,
                    "category": p.category.name if p.category else "",
                    "stock": p.quantity,
                }
                for p in products
            ]
        }
    )


@perm_required("can_manage_stock")
def category_suggest(request):
    """Suggestions de categories pour l'autocompletion."""
    query = request.GET.get("q", "").strip()[:60]
    categories = request.shop.categories.annotate(
        nb_produits=Count("products")
    )
    if query:
        categories = categories.filter(name__icontains=query)
    return JsonResponse(
        {
            "results": [
                {
                    "id": c.pk,
                    "name": c.name,
                    "sku": "",
                    "category": "",
                    "stock": c.nb_produits,
                    "badge": "produit(s)",
                }
                for c in categories.order_by("name")[:12]
            ]
        }
    )


# ---------- Mouvements de stock ----------
@perm_required("can_view_products")
def movement_list(request):
    qs = StockMovement.objects.filter(product__shop=request.shop).select_related(
        "product", "user"
    )

    # Filtrer par recherche
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q)
            | Q(product__sku__icontains=q)
            | Q(note__icontains=q)
            | Q(user__username__icontains=q)
        )

    # Filtrer par type de mouvement
    kind = request.GET.get("type", "")
    if kind in (StockMovement.IN, StockMovement.OUT):
        qs = qs.filter(kind=kind)

    # Filtrer par produit
    product_id = request.GET.get("product", "")
    if product_id.isdigit():
        qs = qs.filter(product_id=product_id)

    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "movement_list.html",
        {
            "page": page,
            "products": Product.objects.filter(shop=request.shop).order_by("name"),
            "q": q,
            "kind": kind,
            "product_id": product_id,
            "qs": params.urlencode(),
        },
    )


@perm_required("can_view_products")
@require_GET
def search_movements(request):
    query = request.GET.get("q", "").strip()
    qs = StockMovement.objects.filter(product__shop=request.shop).select_related(
        "product", "user"
    )
    if query:
        qs = qs.filter(
            Q(product__name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(note__icontains=query)
            | Q(product__sku__icontains=query)
        )
    movements = qs.all()
    data = []
    for m in movements:
        data.append(
            {
                "product": m.product.name,
                "kind": m.get_kind_display(),
                "quantity": m.quantity,
                "note": m.note,
                "user": m.user.username if m.user else "—",
                "created_at": m.created_at.strftime("%d/%m/%Y %H:%M"),
            }
        )
    return JsonResponse({"movements": data})


@perm_required("can_manage_stock")
def movement_create(request):
    initial = {}
    if request.GET.get("product", "").isdigit():
        initial["product"] = request.GET["product"]
    
    form = MovementForm(request.POST or None, shop=request.shop, initial=initial)
    
    # Récupérer les produits et catégories pour le template
    products = Product.objects.filter(shop=request.shop).order_by("name")
    categories = Category.objects.filter(shop=request.shop).order_by("name")
    
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        p = cd["product"]
        kind = cd["kind"]
        record_movement(p, kind, cd["quantity"], cd["note"], request.user)
        p.refresh_from_db()
        push_notification(
            p,
            Notification.STOCK_IN
            if kind == StockMovement.IN
            else Notification.STOCK_OUT,
            user=request.user,
            message=f"{'Entrée' if kind == StockMovement.IN else 'Sortie'} de "
            f"{cd['quantity']} — {p.name} ({p.quantity} en stock)",
        )
        messages.success(request, "Mouvement enregistré.")
        return redirect("movement_list")
    
    return render(
        request,
        "movement_create.html",
        {
            "form": form,
            "products": products,
            "categories": categories,
        },
    )


# ---------- Notifications ----------
@perm_required("can_view_products")
def notification_list(request):
    # Le filtrage (couleur, "non lues", recherche) et la pagination sont
    # faits en JavaScript : la vue envoie un lot de notifications déjà rendu.
    qs = request.shop.notifications.select_related("product", "user")
    total = qs.count()
    notifications = list(qs[:NOTIFICATION_FEED_LIMIT])
    return render(
        request,
        "notification_list.html",
        {
            "notifications": notifications,
            "total": total,
            "truncated": max(total - len(notifications), 0),
            # Etat initial des filtres (repris depuis l'URL, appliqué par le JS).
            "unread": bool(request.GET.get("unread")),
            "level": request.GET.get("level", ""),
            "q": request.GET.get("q", "").strip(),
        },
    )


# ---------- Scanner de codes-barres ----------
def _scan_payload(product):
    """Données d'un produit renvoyées par l'API de scan."""
    return {
        "found": True,
        "id": product.pk,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "category": product.category.name if product.category else "",
        "stock": product.quantity,
        "sale_price": str(product.sale_price),
        "level": product.level,
    }


@perm_required("can_view_products")
@require_GET
@scanner_required
def scan_api(request):
    """GET /api/scan/?code=XXX : retrouve un produit par code-barres, puis par référence.

    La recherche est limitée à la boutique du membre : un code d'une autre
    boutique est traité comme inconnu.
    """
    code = "".join(request.GET.get("code", "").split())[:64]
    if not code:
        return JsonResponse({"found": False, "message": "Aucun code reçu."})
    product = (
        request.shop.products.select_related("category")
        .filter(barcode=code)
        .first()
    )
    if product is None:
        product = (
            request.shop.products.select_related("category").filter(sku=code).first()
        )
    if product is None:
        return JsonResponse({"found": False, "code": code})
    return JsonResponse(_scan_payload(product))


@perm_required("can_manage_stock")
@require_POST
@scanner_required
def scan_movement_api(request):
    """POST /api/scan/mouvement/ : enregistre un lot d'entrées / sorties scanné.

    Le lot est atomique : si une ligne est refusée (produit d'une autre boutique,
    quantité invalide, stock insuffisant), rien n'est enregistré.
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "errors": ["Corps de requête illisible."]}, status=400)

    kind = payload.get("kind")
    if kind not in (StockMovement.IN, StockMovement.OUT):
        return JsonResponse(
            {"ok": False, "errors": ['Type de mouvement invalide : utilisez "IN" ou "OUT".']},
            status=400,
        )

    lines = payload.get("items") or []
    if not isinstance(lines, list) or not lines:
        return JsonResponse({"ok": False, "errors": ["Aucune ligne à enregistrer."]}, status=400)

    note = str(payload.get("note") or "")[:200]
    errors, prepared = [], []
    # Toutes les lignes sont vérifiées avant le moindre enregistrement.
    for index, line in enumerate(lines, start=1):
        if not isinstance(line, dict):
            errors.append(f"Ligne {index} : format invalide.")
            continue
        raw_qty = line.get("quantity")
        try:
            qty = int(raw_qty)
        except (TypeError, ValueError):
            errors.append(f"Ligne {index} : la quantité doit être un nombre entier.")
            continue
        if qty < 1:
            errors.append(f"Ligne {index} : la quantité doit être au moins 1.")
            continue
        product = request.shop.products.filter(pk=line.get("product_id")).first()
        if product is None:
            errors.append(f"Ligne {index} : produit introuvable dans cette boutique.")
            continue
        if kind == StockMovement.OUT and qty > product.quantity:
            errors.append(
                f"Ligne {index} — {product.name} : stock insuffisant "
                f"(disponible : {product.quantity})."
            )
            continue
        prepared.append((product, qty))

    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    is_in = kind == StockMovement.IN
    summary = []
    with transaction.atomic():
        for product, qty in prepared:
            record_movement(product, kind, qty, note, request.user)
            product.refresh_from_db()
            push_notification(
                product,
                Notification.STOCK_IN if is_in else Notification.STOCK_OUT,
                user=request.user,
                message=f"{'Entrée' if is_in else 'Sortie'} de {qty} — "
                f"{product.name} ({product.quantity} en stock)",
            )
            summary.append(
                {
                    "id": product.pk,
                    "name": product.name,
                    "quantity": qty,
                    "stock": product.quantity,
                    "level": product.level,
                }
            )

    return JsonResponse({"ok": True, "kind": kind, "count": len(summary), "items": summary})


@perm_required("can_view_products")
@scanner_required
def scan(request):
    """Page de scan : sortie, entrée ou simple fiche produit."""
    return render(
        request,
        "scan.html",
        {
            "can_manage": request.membership.has("can_manage_stock"),
            "can_add": request.membership.has("can_add_products"),
            "can_edit": request.membership.has("can_edit_products"),
        },
    )


# ---------- Suggestions automatiques (recherche) ----------
def _suggest_q(request, max_len=60):
    return request.GET.get("q", "").strip()[:max_len]


@perm_required("can_view_products")
@require_GET
def suggest_products(request):
    q = _suggest_q(request)
    qs = request.shop.products.select_related("category")
    if q:
        # Nom, référence ou catégorie : la suggestion suit le même périmètre
        # que la recherche de la liste des produits.
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(sku__icontains=q)
            | Q(category__name__icontains=q)
        )
    rows = qs.order_by("name")[:8]
    return JsonResponse(
        {
            "results": [
                {
                    "label": p.name,
                    "sub": " — ".join(x for x in [p.sku, p.category.name if p.category else ""] if x),
                    "value": p.name,
                }
                for p in rows
            ]
        }
    )


# Visible par tout utilisateur autorisé à voir les produits : le filtre de la
# liste doit pouvoir chercher une catégorie même sans le droit d'en gérer.
@perm_required("can_view_products")
@require_GET
def suggest_categories(request):
    q = _suggest_q(request)
    qs = request.shop.categories.annotate(n_products=Count("products"))
    if q:
        qs = qs.filter(name__icontains=q)
    rows = qs.order_by("name")[:8]
    return JsonResponse(
        {
            "results": [
                {
                    "label": c.name,
                    "sub": f"{c.n_products} produit{'s' if c.n_products != 1 else ''}",
                    "value": c.name,
                }
                for c in rows
            ]
        }
    )


@perm_required("can_view_products")
@require_GET
def suggest_movements(request):
    q = _suggest_q(request)
    qs = StockMovement.objects.filter(product__shop=request.shop).select_related("product")
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q)
            | Q(product__sku__icontains=q)
            | Q(note__icontains=q)
        )
    rows = qs.order_by("-created_at", "-id")[:8]
    return JsonResponse(
        {
            "results": [
                {
                    "label": m.product.name,
                    "sub": f"{m.get_kind_display()} — {m.quantity}",
                    "value": m.product.name,
                }
                for m in rows
            ]
        }
    )


@owner_required
@require_GET
def suggest_employees(request):
    q = _suggest_q(request)
    qs = request.shop.members.filter(is_owner=False).select_related("user")
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
        )
    rows = qs.order_by("user__username")[:8]
    return JsonResponse(
        {
            "results": [
                {
                    "label": m.user.get_full_name() or m.user.username,
                    "sub": m.user.username,
                    "value": m.user.username,
                }
                for m in rows
            ]
        }
    )


@perm_required("can_view_products")
@require_GET
def suggest_notifications(request):
    q = _suggest_q(request)
    qs = request.shop.notifications.all()
    if q:
        qs = qs.filter(
            Q(message__icontains=q)
            | Q(product__name__icontains=q)
            | Q(label__icontains=q)
        )
    rows = qs.order_by("-created_at", "-id")[:8]
    return JsonResponse(
        {
            "results": [
                {"label": n.message[:80], "sub": n.label, "value": n.message[:60]}
                for n in rows
            ]
        }
    )


@require_POST
@perm_required("can_view_products")
def notification_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, shop=request.shop)
    n.is_read = True
    n.save(update_fields=["is_read"])
    return redirect_next(request, "notification_list")


@require_POST
@perm_required("can_view_products")
def notification_read_all(request):
    count = request.shop.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, f"{count} notification(s) marquée(s) comme lue(s).")
    return redirect_next(request, "notification_list")


@require_POST
@perm_required("can_view_products")
def notification_clear(request):
    count = request.shop.notifications.count()
    request.shop.notifications.all().delete()
    messages.success(request, f"{count} notification(s) supprimée(s).")
    return redirect_next(request, "notification_list")


# ---------- Employés ----------
@owner_required
def employee_list(request):
    members = request.shop.members.filter(is_owner=False).select_related("user")
    q = request.GET.get("q", "").strip()
    if q:
        members = members.filter(
            Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__email__icontains=q)
        )
    # Les gabarits ne peuvent pas appeler une méthode avec un argument
    # (« member.has(perm) »), les permissions accordées sont donc résolues ici.
    rows = [
        {
            "member": m,
            "granted": [label for name, label in PERMISSIONS if m.has(name)],
        }
        for m in members
    ]
    qs = request.GET.copy()
    qs.pop("page", None)
    return render(
        request,
        "employee_list.html",
        {"rows": rows, "perms": PERMISSIONS, "q": q, "qs": qs.urlencode()},
    )


@owner_required
def employee_create(request):
    form = EmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create_user(
                cd["username"],
                password=cd["password"],
                first_name=cd["first_name"],
                last_name=cd["last_name"],
            )
            Membership.objects.create(
                user=user, shop=request.shop, **{n: cd[n] for n, _ in PERMISSIONS}
            )
        messages.success(request, f"Compte « {user.username} » créé.")
        return redirect("employee_list")
    return render(
        request,
        "employee_form.html",
        {"form": form, "title": "Nouvel employé", "perms": PERMISSIONS},
    )


@owner_required
def employee_edit(request, pk):
    m = get_object_or_404(Membership, pk=pk, shop=request.shop, is_owner=False)
    form = EmployeeForm(request.POST or None, user=m.user, membership=m)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        u = m.user
        u.username, u.first_name, u.last_name = (
            cd["username"],
            cd["first_name"],
            cd["last_name"],
        )
        if cd["password"]:
            u.set_password(cd["password"])
        u.save()
        for n, _ in PERMISSIONS:
            setattr(m, n, cd[n])
        m.save()
        messages.success(request, "Employé mis à jour.")
        return redirect("employee_list")
    return render(
        request,
        "employee_form.html",
        {
            "form": form,
            "title": f"Modifier : {m.user.username}",
            "perms": PERMISSIONS,
        },
    )


@require_POST
@owner_required
def employee_delete(request, pk):
    m = get_object_or_404(Membership, pk=pk, shop=request.shop, is_owner=False)
    m.user.delete()
    messages.success(request, "Compte employé supprimé.")
    return redirect_next(request, "employee_list")


# ---------- API profil de l'utilisateur connecte ----------
def _profile_payload(user, membership=None):
    """Reponse JSON de l'API profil : identite, role, boutique et avatar."""
    if membership is None:
        membership = Membership.objects.filter(user=user).select_related("shop").first()
    data = {
        "username": user.get_username(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.get_full_name() or user.get_username(),
        "email": user.email,
        "date_joined": user.date_joined,
        "last_login": user.last_login,
        "avatar": avatar_data(user),
    }
    profile = get_profile(user)
    data.update(
        {
            "phone": profile.phone if profile else "",
            "bio": profile.bio if profile else "",
            "photo_url": data["avatar"]["url"],
            "has_uploaded_photo": bool(profile and profile.photo),
        }
    )
    if membership:
        data.update(
            {
                "shop_name": membership.shop.name,
                "shop_currency": membership.shop.currency,
                "is_owner": membership.is_owner,
                "role": "Propriétaire" if membership.is_owner else "Employé",
                "permissions": [label for name, label in PERMISSIONS if membership.has(name)],
            }
        )
    else:
        data.update({"shop_name": "", "role": "", "permissions": [], "is_owner": False})
    return data


def _profile_form(request, user, files=None):
    return ProfileForm(
        request.POST if request.method == "POST" else None,
        files,
        instance=ensure_profile(user),
    )


@shop_required
@require_GET
def profile_api(request):
    """GET /api/profil/ : caracteristiques du profil connecte."""
    return JsonResponse(_profile_payload(request.user, request.membership))


@shop_required
@require_POST
def profile_api_update(request):
    """POST /api/profil/ : met a jour la photo, le telephone et la bio."""
    form = _profile_form(request, request.user, request.FILES)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)
    form.save()
    payload = _profile_payload(request.user, request.membership)
    # Le nom affichable peut avoir change via allauth, on garde la source de verite.
    payload["full_name"] = request.user.get_full_name() or request.user.get_username()
    return JsonResponse(payload)


@shop_required
@require_POST
def profile_photo_delete(request):
    """POST /api/profil/photo/supprimer/ : retire la photo uploadée."""
    profile = ensure_profile(request.user)
    if profile.photo:
        profile.photo.delete(save=False)
        profile.save(update_fields=["photo", "updated_at"])
    return JsonResponse(_profile_payload(request.user, request.membership))
