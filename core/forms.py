from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from PIL import Image

from .models import (
    EXPENSE_CATEGORIES,
    Category,
    Customer,
    Delivery,
    DeliveryZone,
    Expense,
    Invoice,
    PERMISSIONS,
    Product,
    Profile,
    Shop,
    StockMovement,
    compute_delivery_fee,
)

# Classes communes a tous les champs, pour que les formulaires soient
# homogenes avec le reste de l'interface (Tailwind).
INPUT_CLASSES = (
    "w-full px-4 py-2.5 rounded-lg border bg-white text-sm text-slate-700 "
    "placeholder-slate-400 transition-colors focus:outline-none focus:ring-2"
)
SELECT_CLASSES = INPUT_CLASSES + " pr-10"
CHECKBOX_CLASSES = (
    "h-4 w-4 rounded border-slate-300 text-primary focus:ring-primary "
    "focus:ring-offset-0 cursor-pointer"
)
INVALID_CLASSES = " border-rose-300 focus:border-rose-400 focus:ring-rose-100"


class StyledFormMixin:
    """Applique les classes Tailwind de l'interface a chaque widget du formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                classes = CHECKBOX_CLASSES
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                classes = SELECT_CLASSES
            else:
                classes = INPUT_CLASSES
            # Les classes deja definies (ex. par un widget declare) sont conservees.
            widget.attrs["class"] = (widget.attrs.get("class", "") + " " + classes).strip()

    def full_clean(self):
        # Validation terminee seulement : les sous-classes ont pu initialiser
        # leurs propres attributs, et les widgets sont lus au moment du rendu.
        super().full_clean()
        for name in self._errors:
            widget = self.fields[name].widget
            widget.attrs["class"] = (widget.attrs.get("class", "") + " " + INVALID_CLASSES).strip()


class ColorInput(forms.TextInput):
    input_type = "color"


def clean_image_upload(upload, max_bytes, max_label, allowed_types, formats_label, field_label):
    """Valide une image envoyee dans un formulaire.

    Le meme controle est applique a la photo de profil et au favicon :
    taille maxi, type MIME, puis ouverture par Pillow (un fichier renomme
    ``.png`` sans etre une image est refuse).
    """
    if not isinstance(upload, UploadedFile):
        # Champ vide : renvoie le fichier deja enregistree (FieldFile). Il a deja
        # ete valide, et surtout l'ouvrir laisserait un verrou sur le fichier.
        return upload
    if upload.size > max_bytes:
        raise forms.ValidationError(f"{field_label} trop lourde ({max_label} maximum).")
    content_type = getattr(upload, "content_type", "") or ""
    if content_type and content_type not in allowed_types:
        raise forms.ValidationError(f"Format non supporté ({formats_label}).")
    try:
        with Image.open(upload) as image:
            image.verify()
    except Exception:
        raise forms.ValidationError("Fichier image invalide.")
    # verify() laisse le curseur en fin de fichier : on le reboucle pour l'enregistrement.
    upload.seek(0)
    return upload


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label="Nom complet", max_length=60, required=False)
    email = forms.EmailField(label="Email", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "email")


class ShopCreateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Shop
        fields = ["name", "address", "phone", "currency", "logo", "primary_color", "sidebar_color", "header_color", "background_color"]
        widgets = {
            "primary_color": ColorInput(),
            "sidebar_color": ColorInput(),
            "header_color": ColorInput(),
            "background_color": ColorInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for color fields
        for field_name in ["primary_color", "sidebar_color", "header_color", "background_color"]:
            if field_name in self.fields:
                self.fields[field_name].initial = Shop._meta.get_field(field_name).default
                # Ces couleurs ont une valeur par defaut : le formulaire ne doit pas
                # etre refuse si le navigateur n'envoie pas le champ.
                self.fields[field_name].required = False

    def clean(self):
        cleaned = super().clean()
        for field_name in ("primary_color", "sidebar_color", "header_color", "background_color"):
            if not cleaned.get(field_name):
                cleaned[field_name] = Shop._meta.get_field(field_name).default
        return cleaned

    @property
    def color_fields(self):
        return [self[n] for n in ["primary_color", "sidebar_color", "header_color", "background_color"]]


class ShopSettingsForm(StyledFormMixin, forms.ModelForm):
    # Un favicon est charge a chaque onglet du navigateur : on refuse les
    # gros fichiers, l/upload inutile de plusieurs Mo serait lent pour tous.
    MAX_FAVICON_BYTES = 256 * 1024  # 256 Ko
    ALLOWED_FAVICON_TYPES = {"image/png", "image/jpeg", "image/x-icon", "image/vnd.microsoft.icon"}

    class Meta:
        model = Shop
        fields = ["name", "address", "phone", "currency", "logo", "favicon", "scanner_enabled",
                  "barcode_field_enabled", "delivery_fee", "delivery_free_threshold",
                  "delivery_min_amount",
                  "primary_color", "sidebar_color",
                  "header_color", "background_color"]
        widgets = {f: ColorInput() for f in ["primary_color", "sidebar_color", "header_color", "background_color"]}

    # Interrupteurs dessines a la main dans la page des parametres : une case
    # non cochee ne doit pas etre lue comme « desactiver la fonctionnalite ».
    TOGGLES = ("scanner_enabled", "barcode_field_enabled")
    # Champs de livraison : gardent leur valeur actuelle quand ils ne sont pas envoyes.
    OPTIONAL_KEEP = ("delivery_fee", "delivery_free_threshold", "delivery_min_amount")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.TOGGLES:
            self.fields[name].required = False
            if not self.is_bound:
                self.fields[name].initial = Shop._meta.get_field(name).default
        for name in self.OPTIONAL_KEEP:
            self.fields[name].required = False

    def clean(self):
        cleaned = super().clean()
        for name in self.OPTIONAL_KEEP:
            if name in self.fields and cleaned.get(name) is None:
                cleaned[name] = getattr(self.instance, name)
        return cleaned

    def clean_favicon(self):
        return clean_image_upload(
            self.cleaned_data.get("favicon"),
            max_bytes=self.MAX_FAVICON_BYTES,
            max_label="256 Ko",
            allowed_types=self.ALLOWED_FAVICON_TYPES,
            formats_label="PNG, JPEG ou ICO",
            field_label="Icône du site",
        )

    @property
    def info_fields(self):
        return [self[n] for n in ["name", "address", "phone", "currency", "logo", "favicon"]]

    @property
    def color_fields(self):
        return [self[n] for n in ["primary_color", "sidebar_color", "header_color", "background_color"]]


class ProfileForm(StyledFormMixin, forms.ModelForm):
    """Edition du profil connecte : photo, telephone et bio."""

    MAX_PHOTO_BYTES = 2 * 1024 * 1024  # 2 Mo
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

    class Meta:
        model = Profile
        fields = ["photo", "phone", "bio"]
        widgets = {"bio": forms.TextInput(attrs={"maxlength": 200})}

    def clean_photo(self):
        return clean_image_upload(
            self.cleaned_data.get("photo"),
            max_bytes=self.MAX_PHOTO_BYTES,
            max_label="2 Mo",
            allowed_types=self.ALLOWED_TYPES,
            formats_label="JPEG, PNG, WebP ou GIF",
            field_label="Photo",
        )

    @property
    def info_fields(self):
        return [self[n] for n in ["phone", "bio"]]


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "barcode", "category", "cost_price", "sale_price", "quantity", "alert_threshold", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            # Espace pour l'icone de code-barres pose devant le champ.
            "barcode": forms.TextInput(attrs={"class": "pl-10", "autocomplete": "off"}),
        }

    def __init__(self, *args, shop, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.fields["category"].queryset = shop.categories.all().order_by("name")
        _autocomplete(self.fields["category"], CategoryAutocompleteWidget)
        self.fields["sku"].help_text = "Laisser vide pour générer automatiquement."
        if shop.barcode_field_enabled:
            self.fields["barcode"].help_text = "Facultatif — scannable ensuite depuis le menu Scanner."
        else:
            # Champ retire des deux formulaires produit : le code n'est alors
            # saisi que par le menu Scanner, qui le renvoie dans l'URL. Le champ
            # disparait aussi de la validation, et le code deja enregistre est
            # conserve tel quel a l'edition.
            del self.fields["barcode"]
        if self.instance.pk:
            self.fields["quantity"].label = "Quantité en stock"
            self.fields["quantity"].help_text = (
                "Toute correction est enregistrée comme ajustement dans l'historique."
            )
        else:
            self.fields["quantity"].label = "Stock initial"
            self.fields["quantity"].help_text = "Quantité de départ du produit."

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip()
        if sku:
            qs = Product.objects.filter(shop=self.shop, sku=sku).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Cette référence existe déjà.")
        return sku

    def clean_barcode(self):
        # Meme normalisation que Product.save(), pour que la verification
        # d'unicite porte sur la valeur reellement enregistree.
        barcode = "".join((self.cleaned_data.get("barcode") or "").split())
        if barcode:
            qs = Product.objects.filter(shop=self.shop, barcode=barcode).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f"Le code-barres {barcode} est déjà attribué à un autre produit de cette boutique."
                )
        return barcode

    def clean_quantity(self):
        q = self.cleaned_data["quantity"]
        if q < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return q


class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class AutocompleteSelect(forms.Select):
    """Select enrichi d'une saisie avec suggestions temps reel (aucun rechargement).

    Le <select> d'origine reste dans la page (il porte encore le nom du champ et
    assure la validation cote serveur) ; il est simplement replie dans un <details>.
    """

    template_name = "core/widgets/product_autocomplete.html"
    endpoint_name = ""
    search_placeholder = "Rechercher..."
    kind = ""

    def get_context(self, name, value, attrs):
        from django.urls import reverse

        ctx = super().get_context(name, value, attrs)
        widget = ctx["widget"]
        widget["endpoint"] = reverse(self.endpoint_name)
        widget["kind"] = self.kind
        widget["search_id"] = "product-search-%s" % name
        widget["selected_label"] = ""
        widget["search_placeholder"] = self.search_placeholder

        for _group, choices, _index in widget.get("optgroups", []):
            for option in choices:
                # On ignore l'option vide ("- Choisir une option -").
                if option.get("selected") and option.get("value") not in ("", None):
                    widget["selected_label"] = str(option.get("label", "")).strip()
                    break
            if widget["selected_label"]:
                break

        return ctx


class ProductAutocompleteWidget(AutocompleteSelect):
    endpoint_name = "product_suggest"
    search_placeholder = "Rechercher un produit par nom, SKU ou categorie..."
    kind = "product"


class CategoryAutocompleteWidget(AutocompleteSelect):
    endpoint_name = "category_suggest"
    search_placeholder = "Rechercher une categorie..."
    kind = "category"


class CustomerAutocompleteWidget(AutocompleteSelect):
    endpoint_name = "suggest_customers"
    search_placeholder = "Rechercher un client (nom, téléphone, adresse)..."
    kind = "customer"


class ZoneSelect(forms.Select):
    """Select des zones qui expose le tarif et le mode manuel aux options.

    Le formulaire de livraison s'en sert en JavaScript pour pré-remplir le prix
    ou l'activer pour les livraisons hors Brazzaville (montant manuel).
    """

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        zone = getattr(value, "instance", None)
        if zone is not None:
            option["attrs"]["data-fee"] = str(zone.fee)
            option["attrs"]["data-manual"] = "1" if zone.is_manual else "0"
        return option


def _autocomplete(field, widget_class):
    """Remplace le widget d'un champ par sa version avec suggestions, en gardant le style."""
    field.widget = widget_class(attrs=dict(field.widget.attrs), choices=field.choices)
    return field


class MovementForm(StyledFormMixin, forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Catégorie",
        help_text="Facultatif : filtre la liste des produits.",
    )

    class Meta:
        model = StockMovement
        fields = ["product", "kind", "quantity", "note"]

    def __init__(self, *args, shop, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = shop.products.all().order_by("name")
        self.fields["category"].queryset = shop.categories.all().order_by("name")
        self.fields["quantity"].min_value = 1
        # Le ModelChoiceIterator du champ porte les choix : il faut le transferer
        # au nouveau widget, sinon la liste de repli reste vide.
        _autocomplete(self.fields["product"], ProductAutocompleteWidget)
        _autocomplete(self.fields["category"], CategoryAutocompleteWidget)

    def clean(self):
        cd = super().clean()
        p, kind, qty = cd.get("product"), cd.get("kind"), cd.get("quantity")
        if p and kind == StockMovement.OUT and qty and qty > p.quantity:
            self.add_error("quantity", f"Stock insuffisant (disponible : {p.quantity}).")
        if qty is not None and qty < 1:
            self.add_error("quantity", "La quantité doit être au moins 1.")
        return cd


class EmployeeForm(StyledFormMixin, forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    first_name = forms.CharField(label="Prénom", max_length=60, required=False)
    last_name = forms.CharField(label="Nom", max_length=60, required=False)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=False)

    def __init__(self, *args, user=None, membership=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_obj = user
        for name, label in PERMISSIONS:
            if membership:
                initial = getattr(membership, name)
            else:
                # Cree un nouveau compte : lecture et caisse ouvertes par defaut.
                initial = name in ("can_view_products", "can_print_tickets")
            self.fields[name] = forms.BooleanField(
                label=label,
                required=False,
                initial=initial,
                widget=forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            )
        if user is None:
            self.fields["password"].required = True
        else:
            self.fields["password"].help_text = "Laisser vide pour ne pas changer."
            self.initial.update(username=user.username, first_name=user.first_name, last_name=user.last_name)

    def clean_username(self):
        v = self.cleaned_data["username"]
        qs = User.objects.filter(username__iexact=v)
        if self.user_obj:
            qs = qs.exclude(pk=self.user_obj.pk)
        if qs.exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return v

    def clean_password(self):
        pw = self.cleaned_data["password"]
        if pw:
            validate_password(pw, self.user_obj)
        return pw

    @property
    def info_fields(self):
        return [self[n] for n in ["username", "first_name", "last_name", "password"]]

    @property
    def perm_fields(self):
        return [self[n] for n, _ in PERMISSIONS]


# ---------- Clients, factures, livraisons ----------
class CustomerForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "address", "note"]

    def __init__(self, *args, shop, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Le nom du client est obligatoire.")
        return name


class ExpenseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["label", "amount", "category", "spent_at", "note"]
        widgets = {
            "spent_at": forms.DateInput(attrs={"type": "date"}),
            "category": forms.Select(choices=EXPENSE_CATEGORIES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields["spent_at"].initial = timezone.localdate()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return amount


class InvoiceLineForm(StyledFormMixin, forms.Form):
    """Une ligne « produit » d'une facture : produit, quantité, prix payé."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(), label="Produit", empty_label=None
    )
    quantity = forms.IntegerField(label="Quantité", min_value=1, initial=1)
    unit_price = forms.DecimalField(label="Prix unitaire", max_digits=12, decimal_places=2,
                                    required=False)

    def __init__(self, *args, shop, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = shop.products.all().order_by("name")
        _autocomplete(self.fields["product"], ProductAutocompleteWidget)
        self.fields["unit_price"].help_text = "Laisser vide pour le prix de vente du produit."

    def clean(self):
        cd = super().clean()
        product = cd.get("product")
        if product is not None and cd.get("unit_price") is None:
            # Prix de vente courant du produit, ajustable à la saisie.
            cd["unit_price"] = product.sale_price
        return cd


InvoiceLineFormSet = forms.formset_factory(
    InvoiceLineForm, extra=3, can_delete=True, min_num=1, validate_min=True
)


class InvoiceHeaderForm(StyledFormMixin, forms.ModelForm):
    """En-tête d'une facture : client (facultatif, achat anonyme) et note."""

    class Meta:
        model = Invoice
        fields = ["customer", "note"]

    def __init__(self, *args, shop, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.fields["customer"].queryset = shop.customers.all().order_by("name")
        self.fields["customer"].required = False
        _autocomplete(self.fields["customer"], CustomerAutocompleteWidget)


class DeliveryForm(StyledFormMixin, forms.ModelForm):
    name = forms.CharField(label="Nom du client", max_length=150, required=False)
    phone = forms.CharField(label="Téléphone", max_length=40, required=False)
    zone = forms.ModelChoiceField(
        queryset=DeliveryZone.objects.none(),
        label="Arrondissement / Département",
        required=False,
        widget=ZoneSelect,
    )

    class Meta:
        model = Delivery
        fields = ["invoice", "zone", "address", "scheduled_for", "fee", "note"]
        widgets = {
            "scheduled_for": forms.DateInput(attrs={"type": "date"}),
            "address": forms.TextInput(attrs={"placeholder": "Quartier, rue ou ville (si hors zone)"}),
        }

    def __init__(self, *args, shop, movement=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.movement = movement
        self.fields["invoice"].queryset = shop.invoices.select_related("customer").order_by(
            "-created_at"
        )
        self.fields["invoice"].required = False
        self.fields["invoice"].empty_label = "Aucune facture liée"

        self.fields["zone"].queryset = shop.delivery_zones.filter(deleted_at__isnull=True).order_by("name")
        self.fields["zone"].empty_label = "Choisir un arrondissement / département"

        self.fields["address"].required = False
        self.fields["fee"].required = False

        instance = kwargs.get("instance")
        if instance:
            if instance.customer:
                self.fields["name"].initial = instance.customer.name
                self.fields["phone"].initial = instance.customer.phone
            if instance.invoice and instance.invoice.customer:
                cust = instance.invoice.customer
                self.fields["name"].initial = self.fields["name"].initial or cust.name
                self.fields["phone"].initial = self.fields["phone"].initial or cust.phone
            return

        # Facture transmise (?facture=<pk>) : le client est récupéré d'office.
        invoice = self.initial.get("invoice")
        if invoice is not None:
            self.fields["invoice"].initial = invoice.pk
            if invoice.customer:
                self.fields["name"].initial = invoice.customer.name
                self.fields["phone"].initial = invoice.customer.phone

    def _source_total(self, invoice):
        """Montant qui conditionne la livraison : total de la facture ou valeur de la sortie."""
        if invoice is not None:
            return invoice.total
        if self.movement is not None:
            return self.movement.product.sale_price * self.movement.quantity
        return None

    def _free_delivery(self, invoice):
        """Livraison retirée (offerte) : dépense cumulée du client ou montant atteint."""
        customer = invoice.customer if invoice else None
        if customer is not None and customer.free_delivery:
            return True
        threshold = self.shop.delivery_free_threshold
        total = self._source_total(invoice)
        if threshold and threshold > 0 and total is not None and total >= threshold:
            return True
        return False

    def clean(self):
        cd = super().clean()
        invoice = cd.get("invoice")
        zone = cd.get("zone")
        name = (cd.get("name") or "").strip()
        phone = (cd.get("phone") or "").strip()
        fee = cd.get("fee")
        address = (cd.get("address") or "").strip()

        if invoice and invoice.shop_id != self.shop.pk:
            self.add_error("invoice", "Cette facture n'appartient pas à votre boutique.")

        # Le client est repris de la facture quand elle en a un.
        if invoice and invoice.customer:
            name = name or invoice.customer.name
            phone = phone or invoice.customer.phone

        # Montant minimum : la livraison n'est valide qu'au-delà du seuil défini.
        # Le montant vient de la facture liée ou, à défaut, de la sortie de stock.
        min_amount = self.shop.delivery_min_amount
        total = self._source_total(invoice)
        if min_amount > 0 and total is None:
            self.add_error(
                "invoice",
                "Liez une facture ou une sortie de stock pour vérifier le montant minimum de livraison.",
            )
        elif min_amount > 0 and total is not None and total < min_amount:
            source = "facture" if invoice is not None else "sortie"
            self.add_error(
                "invoice" if invoice is not None else None,
                f"Le montant de la {source} ({total} {self.shop.currency}) est inférieur au minimum "
                f"({min_amount} {self.shop.currency}) requis pour la livraison.",
            )

        if not zone:
            self.add_error("zone", "Veuillez sélectionner l'arrondissement ou le département.")

        if zone and zone.is_manual:
            # Hors Brazzaville : le montant est saisi à la main.
            if fee is None or fee < 0:
                self.add_error("fee", "Veuillez saisir le prix de livraison pour cette zone (hors Brazzaville).")
            else:
                cd["fee"] = fee
        elif self._free_delivery(invoice):
            # Seuil atteint : le prix de livraison est directement retiré.
            cd["fee"] = Decimal("0")
        elif zone:
            if fee is None:
                fee = zone.fee
            if fee < 0:
                self.add_error("fee", "Le prix ne peut pas être négatif.")
            else:
                cd["fee"] = fee
        else:
            if fee is None:
                fee = compute_delivery_fee(self.shop, None)
            if fee < 0:
                self.add_error("fee", "Le prix ne peut pas être négatif.")
            else:
                cd["fee"] = fee

        if not name:
            self.add_error("name", "Le nom du client est requis.")

        if not address and zone:
            address = zone.name

        cd["name"] = name
        cd["phone"] = phone
        cd["address"] = address
        cd["zone"] = zone
        return cd

    def save(self, commit=True):
        delivery = super().save(commit=False)
        if self.movement is not None and not delivery.movement_id:
            delivery.movement = self.movement
        invoice = self.cleaned_data.get("invoice")
        if invoice and invoice.customer:
            delivery.customer = invoice.customer
        elif not delivery.customer_id:
            delivery.customer = self._resolve_customer(
                self.cleaned_data.get("name", ""), self.cleaned_data.get("phone", "")
            )
        if commit:
            delivery.save()
        return delivery

    def _resolve_customer(self, name, phone):
        """Retrouve ou crée la fiche client à partir du nom et du téléphone saisis."""
        name = (name or "").strip()
        phone = (phone or "").strip()
        if not name and not phone:
            return None
        if phone:
            existing = self.shop.customers.filter(phone=phone).first()
            if existing:
                return existing
        if name:
            existing = self.shop.customers.filter(name__iexact=name).first()
            if existing:
                if phone and not existing.phone:
                    existing.phone = phone
                    existing.save(update_fields=["phone"])
                return existing
        return self.shop.customers.create(name=name or phone, phone=phone)


class DeliveryZoneForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = ["name", "fee", "is_manual"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex. Talangaï (6e)"}),
        }

    def __init__(self, *args, shop, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Le nom de la zone est obligatoire.")
        qs = DeliveryZone.objects.filter(shop=self.shop, name=name).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cette zone existe déjà.")
        return name

    def clean_fee(self):
        fee = self.cleaned_data.get("fee")
        if fee is None:
            return Decimal("0")
        if fee < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        return fee
