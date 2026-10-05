from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from .models import PERMISSIONS, Category, Product, Profile, Shop, StockMovement

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


class ShopSettingsForm(StyledFormMixin, forms.ModelForm):
    # Un favicon est charge a chaque onglet du navigateur : on refuse les
    # gros fichiers, l/upload inutile de plusieurs Mo serait lent pour tous.
    MAX_FAVICON_BYTES = 256 * 1024  # 256 Ko
    ALLOWED_FAVICON_TYPES = {"image/png", "image/jpeg", "image/x-icon", "image/vnd.microsoft.icon"}

    class Meta:
        model = Shop
        fields = ["name", "address", "phone", "currency", "logo", "favicon", "scanner_enabled",
                  "barcode_field_enabled", "primary_color", "sidebar_color",
                  "header_color", "background_color"]
        widgets = {f: ColorInput() for f in ["primary_color", "sidebar_color", "header_color", "background_color"]}

    # Interrupteurs dessines a la main dans la page des parametres : une case
    # non cochee ne doit pas etre lue comme « desactiver la fonctionnalite ».
    TOGGLES = ("scanner_enabled", "barcode_field_enabled")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.TOGGLES:
            self.fields[name].required = False
            if not self.is_bound:
                self.fields[name].initial = Shop._meta.get_field(name).default

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
            initial = getattr(membership, name) if membership else name == "can_view_products"
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
