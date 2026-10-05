from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import Q

hex_color = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Couleur invalide (format #rrggbb).")

# (champ, libellé) — utilisé par les formulaires et les décorateurs
PERMISSIONS = [
    ("can_view_products", "Voir les produits"),
    ("can_add_products", "Ajouter des produits"),
    ("can_edit_products", "Modifier des produits"),
    ("can_delete_products", "Supprimer des produits"),
    ("can_manage_stock", "Gérer le stock (entrées / sorties)"),
    ("can_manage_categories", "Gérer les catégories"),
]

# kind de notification -> (libellé, code son, fréquence du bip en Hz)
NOTIFICATION_KINDS = {
    "ADDED": ("Produit ajouté", "AJOUT", 880),
    "IN": ("Entrée de stock", "ENTREE", 660),
    "OUT": ("Sortie de stock", "SORTIE", 440),
    "LOW": ("Stock bas", "BAS", 523),
    "RUPT": ("Rupture de stock", "RUPTURE", 294),
    "ADJ": ("Quantité ajustée", "AJUST", 740),
}

# Code couleur du niveau de quantité : (fond, texte).
LEVEL_COLORS = {
    "rupture": ("#fadbd8", "#b03a2e"),
    "bas": ("#fdecd2", "#b8730f"),
    "ok": ("#e3f4d6", "#4c8a1f"),
}


class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops")
    name = models.CharField("Nom de la boutique", max_length=120)
    address = models.CharField("Adresse", max_length=200, blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    currency = models.CharField("Devise", max_length=10, default="FCFA")
    logo = models.ImageField("Logo", upload_to="logos/", blank=True, null=True)
    primary_color = models.CharField("Couleur principale", max_length=7, default="#5bc0de", validators=[hex_color])
    sidebar_color = models.CharField("Couleur du menu latéral", max_length=7, default="#3d4b5c", validators=[hex_color])
    header_color = models.CharField("Couleur des en-têtes de tableau", max_length=7, default="#4a5868", validators=[hex_color])
    background_color = models.CharField("Couleur de fond", max_length=7, default="#e9edf4", validators=[hex_color])
    # Le scanner est facultatif : une boutique peut le masquer completement
    # (menu, page et API) depuis ses parametres.
    scanner_enabled = models.BooleanField("Scanner de codes-barres", default=True)

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return self.name[:3].upper()


class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="membership")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="members")
    is_owner = models.BooleanField(default=False)
    can_view_products = models.BooleanField(default=True)
    can_add_products = models.BooleanField(default=False)
    can_edit_products = models.BooleanField(default=False)
    can_delete_products = models.BooleanField(default=False)
    can_manage_stock = models.BooleanField(default=False)
    can_manage_categories = models.BooleanField(default=False)

    def has(self, perm):
        return self.is_owner or bool(getattr(self, perm, False))

    def __str__(self):
        return f"{self.user} @ {self.shop}"


class Profile(models.Model):
    """Photo et informations complementaires de l'utilisateur connecte.

    La photo est facultative : l'interface affiche alors les initiales
    (voir core.avatar.user_initials).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Utilisateur")
    photo = models.ImageField("Photo de profil", upload_to="profiles/", blank=True, null=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    bio = models.CharField("Bio", max_length=200, blank=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user}"


class Category(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField("Nom", max_length=80)

    class Meta:
        ordering = ["name"]
        unique_together = ("shop", "name")
        verbose_name_plural = "catégories"

    def __str__(self):
        return self.name


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="products", verbose_name="Catégorie")
    name = models.CharField("Nom du produit", max_length=150)
    sku = models.CharField("Référence", max_length=40, blank=True)
    barcode = models.CharField("Code-barres", max_length=64, blank=True, db_index=True)
    cost_price = models.DecimalField("Prix d'achat", max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField("Prix de vente", max_digits=12, decimal_places=2, default=0)
    quantity = models.IntegerField("Quantité en stock", default=0)
    alert_threshold = models.PositiveIntegerField("Seuil d'alerte", default=5)
    description = models.TextField("Description", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("shop", "sku")
        constraints = [
            # Un code-barres est unique dans une boutique, mais facultatif :
            # sans condition, plusieurs produits sans code seraient refusés.
            models.UniqueConstraint(
                fields=["shop", "barcode"],
                condition=~Q(barcode=""),
                name="uniq_barcode_per_shop",
            )
        ]

    def __str__(self):
        return self.name

    @property
    def is_low(self):
        return self.quantity <= self.alert_threshold

    @property
    def level(self):
        """Code couleur de la quantité : rupture / bas / sain."""
        if self.quantity <= 0:
            return "rupture"
        return "bas" if self.is_low else "ok"

    def save(self, *args, **kwargs):
        # Les scanners et les Urlcodes lus au clavier arrivent souvent avec des
        # espaces parasites : on normalise avant d'enregistrer.
        if self.barcode is not None:
            self.barcode = "".join(self.barcode.split())
        if not self.sku:
            n = Product.objects.filter(shop=self.shop).count() + 1
            while Product.objects.filter(shop=self.shop, sku=f"PRD-{n:04d}").exists():
                n += 1
            self.sku = f"PRD-{n:04d}"
        super().save(*args, **kwargs)


class Notification(models.Model):
    PRODUCT_ADDED = "ADDED"
    STOCK_IN = "IN"
    STOCK_OUT = "OUT"
    LOW_STOCK = "LOW"
    OUT_OF_STOCK = "RUPT"
    ADJUSTED = "ADJ"

    KIND_CHOICES = [
        (PRODUCT_ADDED, "Produit ajouté"),
        (STOCK_IN, "Entrée de stock"),
        (STOCK_OUT, "Sortie de stock"),
        (LOW_STOCK, "Stock bas"),
        (OUT_OF_STOCK, "Rupture de stock"),
        (ADJUSTED, "Quantité ajustée"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="notifications",
                             verbose_name="Boutique")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE,
                                related_name="notifications", verbose_name="Produit")
    kind = models.CharField("Type", max_length=5, choices=KIND_CHOICES)
    label = models.CharField("Intitulé", max_length=40)
    message = models.CharField("Message", max_length=200)
    quantity = models.IntegerField("Quantité", default=0)
    alert_threshold = models.IntegerField("Seuil", default=0)
    sound_code = models.CharField("Code son", max_length=8)
    level = models.CharField("Niveau", max_length=8, default="ok")
    is_read = models.BooleanField("Lue", default=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"[{self.sound_code}] {self.message}"

    @property
    def colors(self):
        return LEVEL_COLORS.get(self.level, LEVEL_COLORS["ok"])

    @property
    def tone(self):
        return NOTIFICATION_KINDS.get(self.kind, ("", "BIP", 880))[2]


class StockMovement(models.Model):
    IN, OUT = "IN", "OUT"
    KINDS = [(IN, "Entrée"), (OUT, "Sortie")]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements", verbose_name="Produit")
    kind = models.CharField("Type", max_length=3, choices=KINDS)
    quantity = models.PositiveIntegerField("Quantité")
    note = models.CharField("Note", max_length=200, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]


def record_movement(product, kind, qty, note, user):
    """Enregistre un mouvement et met à jour le stock de façon atomique."""
    with transaction.atomic():
        p = Product.objects.select_for_update().get(pk=product.pk)
        before = p.quantity
        p.quantity = before + qty if kind == StockMovement.IN else before - qty
        p.save(update_fields=["quantity"])
        movement = StockMovement.objects.create(
            product=p, kind=kind, quantity=qty, note=note, user=user
        )
    # Alerte de stock seulement au franchissement du seuil, pour éviter de
    # notifier à chaque mouvement tant que le produit reste en alerte.
    notify_threshold_crossing(p, before, user)
    return movement


def record_adjustment(product, previous_qty, user, note="Ajustement manuel"):
    """Trace un ajustement manuel de la quantité comme mouvement.

    Le formulaire a déjà enregistré la nouvelle valeur : previous_qty est donc
    l'ancienne quantité, nécessaire pour calculer l'écart à historiser.
    """
    with transaction.atomic():
        p = Product.objects.select_for_update().get(pk=product.pk)
        p.quantity = max(0, p.quantity)
        p.save(update_fields=["quantity"])
        if p.quantity == previous_qty:
            return None
        kind = StockMovement.IN if p.quantity > previous_qty else StockMovement.OUT
        movement = StockMovement.objects.create(
            product=p, kind=kind, quantity=abs(p.quantity - previous_qty), note=note, user=user
        )
    push_notification(p, Notification.ADJUSTED, user=user)
    notify_threshold_crossing(p, previous_qty, user)
    return movement


# kind -> (libellé, code son, fréquence du bip) — voir NOTIFICATION_KINDS en tête de module.
def push_notification(product, kind, user=None, message=""):
    """Crée une notification et calcule son code couleur d'après la quantité."""
    label, sound, _freq = NOTIFICATION_KINDS[kind]
    if not message:
        message = f"{label} : {product.name} ({product.quantity} en stock)"
    return Notification.objects.create(
        shop=product.shop,
        product=product,
        kind=kind,
        label=label,
        message=message,
        quantity=product.quantity,
        alert_threshold=product.alert_threshold,
        sound_code=sound,
        level=product.level,
        user=user,
    )


def notify_threshold_crossing(product, before, user=None):
    """Alerte sur franchissement de seuil, et sur-escalade vers la rupture.

    Sans cette garde, chaque mouvement génèrerait une notification tant que le
    produit resterait en dessous du seuil.
    """
    if product.quantity <= 0 < before:
        push_notification(product, Notification.OUT_OF_STOCK, user=user)
    elif before > product.alert_threshold >= product.quantity > 0:
        push_notification(product, Notification.LOW_STOCK, user=user)
