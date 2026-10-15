import uuid as uuid_lib
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import DecimalField, F, Q, Sum
from django.utils import timezone
from urllib.parse import quote

hex_color = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Couleur invalide (format #rrggbb).")

# (champ, libellé) — utilisé par les formulaires et les décorateurs
PERMISSIONS = [
    ("can_view_products", "Voir les produits"),
    ("can_add_products", "Ajouter des produits"),
    ("can_edit_products", "Modifier des produits"),
    ("can_delete_products", "Supprimer des produits"),
    ("can_manage_stock", "Gérer le stock (entrées / sorties)"),
    ("can_manage_categories", "Gérer les catégories"),
    ("can_manage_employees", "Gérer les employés"),
    ("can_print_tickets", "Imprimer les tickets de caisse"),
    ("can_manage_settings", "Gérer les paramètres de la boutique"),
    ("can_manage_deliveries", "Gérer les clients et les livraisons"),
]

# Catégories de dépenses de la page Finance.
EXPENSE_CATEGORIES = [
    ("loyer", "Loyer"),
    ("salaire", "Salaire"),
    ("transport", "Transport"),
    ("fournisseur", "Fournisseur"),
    ("energie", "Électricité / Eau"),
    ("autre", "Autre"),
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


# ---------------------------------------------------------------------------
# Support de la synchronisation hors ligne (voir docs/SYNC.md)
# ---------------------------------------------------------------------------
# L'uuid est généré par le client : il désigne la ligne avant même qu'elle
# existe côté serveur, ce qui permet de créer et modifier des données hors ligne.
# Les contraintes d'unicité restent indexed sur les lignes vivantes : une ligne
# supprimée logiquement libère sa référence et son code-barres.

class SyncFieldsMixin(models.Model):
    """Identifiant stable et horodatage de modification."""

    uuid = models.UUIDField("UUID", default=uuid_lib.uuid4, editable=False, unique=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def hard_delete(self):
        return super().delete()

    def soft_delete(self):
        return self.update(deleted_at=timezone.now(), updated_at=timezone.now())

    def restore(self):
        return self.update(deleted_at=None, updated_at=timezone.now())


class LiveManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Manager par défaut : les lignes supprimées logiquement sont masquées.

    Défini en premier, il devient le `_default_manager` du modèle, donc aussi
    celui des managers liés (shop.products, product.movements...). Le web et
    l'API voient ainsi exactement la même liste.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteMixin(SyncFieldsMixin):
    """Suppression logique : la ligne quitte les listes mais reste synchronisable.

    `deleted_at` permet à un autre appareil d'apprendre la suppression par
    synchronisation incrémentale, ce qu'une suppression physique rendrait
    impossible.
    """

    deleted_at = models.DateTimeField("Supprimé le", null=True, blank=True, db_index=True)

    objects = LiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
        return self

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])
        return self


class Shop(SyncFieldsMixin, models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops")
    name = models.CharField("Nom de la boutique", max_length=120)
    address = models.CharField("Adresse", max_length=200, blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    currency = models.CharField("Devise", max_length=10, default="FCFA")
    logo = models.ImageField("Logo", upload_to="logos/", blank=True, null=True)
    favicon = models.ImageField("Icône du site (favicon)", upload_to="favicons/", blank=True, null=True)
    primary_color = models.CharField("Couleur principale", max_length=7, default="#5bc0de", validators=[hex_color])
    sidebar_color = models.CharField("Couleur du menu latéral", max_length=7, default="#3d4b5c", validators=[hex_color])
    header_color = models.CharField("Couleur des en-têtes de tableau", max_length=7, default="#4a5868", validators=[hex_color])
    background_color = models.CharField("Couleur de fond", max_length=7, default="#e9edf4", validators=[hex_color])
    # Le scanner est facultatif : une boutique peut le masquer completement
    # (menu, page et API) depuis ses parametres.
    scanner_enabled = models.BooleanField("Scanner de codes-barres", default=True)
    # Reglee separement de scanner_enabled : une boutique peut garder le menu
    # Scanner (saisie clavier / camera) tout en retirant le champ des
    # formulaires produit, les codes lus etant alors enregistres sans saisie.
    barcode_field_enabled = models.BooleanField("Champ « Code-barres »", default=True)
    # Livraisons : prix par défaut et seuils
    # Seuil d'achat minimum pour autoriser la livraison (0 = désactivé)
    delivery_min_amount = models.DecimalField(
        "Montant minimum d'achat pour la livraison",
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    # Prix par défaut et seuil de dépense cumulée à partir duquel
    # la livraison devient offerte pour le client. Seuil à 0 = désactivé.
    delivery_fee = models.DecimalField(
        "Prix de livraison (par défaut)", max_digits=12, decimal_places=2, default=0
    )
    delivery_free_threshold = models.DecimalField(
        "Seuil de dépense cumulée (livraison offerte)",
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return self.name

    @property
    def initials(self):
        """Initiales pour le logo et le favicon : une lettre par mot.

        « Ma Boutique » donne « MB », et non les trois premiers caracteres
        (« MA »), qui sont coupees au hasard par la coupure des mots.
        """
        letters = "".join(word[0] for word in self.name.split() if word)[:3]
        return (letters or self.name[:3]).upper()

    @property
    def document_title(self):
        """Titre de l'onglet du navigateur : le nom de la société.

        Passe par la propriete plutot que par le nom du modele pour que les
        gabarits aient un point d'entree unique si la regle change.
        """
        return self.name or "Stock"

    @property
    def favicon_url(self):
        """URL du favicon : le logo de la societe, une icone envoyee, ou les initiales.

        L'icone de l'onglet suit automatiquement le logo de la societe : aucune
        manipulation n'est demandee dans les parametres. Une icone envoyee par
        le passe (administration) reste utilisee a defaut de logo. Sans image,
        un SVG d'initiales evite une requete vers /favicon.ico qui repondrait 404.
        """
        if self.logo:
            return self.logo.url
        if self.favicon:
            return self.favicon.url
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
            f"<rect width='64' height='64' rx='14' fill='{self.primary_color}'/>"
            "<text x='32' y='43' text-anchor='middle' font-family='Montserrat,Arial,sans-serif'"
            f" font-size='28' font-weight='bold' fill='#ffffff'>{self.initials}</text>"
            "</svg>"
        )
        return "data:image/svg+xml," + quote(svg, safe="")


class Membership(SyncFieldsMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="membership")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="members")
    is_owner = models.BooleanField(default=False)
    can_view_products = models.BooleanField(default=True)
    can_add_products = models.BooleanField(default=False)
    can_edit_products = models.BooleanField(default=False)
    can_delete_products = models.BooleanField(default=False)
    can_manage_stock = models.BooleanField(default=False)
    can_manage_categories = models.BooleanField(default=False)
    can_manage_employees = models.BooleanField(default=False)
    # Autorise l'impression des tickets de caisse : conservee par defaut pour
    # les employes deja crees, et proposee cochee a la creation d'un compte.
    can_print_tickets = models.BooleanField(default=True)
    can_manage_settings = models.BooleanField(default=False)
    can_manage_deliveries = models.BooleanField(default=False)

    def has(self, perm):
        return self.is_owner or bool(getattr(self, perm, False))

    def __str__(self):
        return f"{self.user} @ {self.shop}"


class Profile(SyncFieldsMixin, models.Model):
    """Photo et informations complementaires de l'utilisateur connecte.

    La photo est facultative : l'interface affiche alors les initiales
    (voir core.avatar.user_initials).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Utilisateur")
    photo = models.ImageField("Photo de profil", upload_to="profiles/", blank=True, null=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    bio = models.CharField("Bio", max_length=200, blank=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user}"


class Category(SoftDeleteMixin, models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField("Nom", max_length=80)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "catégories"
        constraints = [
            # Un nom est unique parmi les catégories vivantes de la boutique.
            # Une catégorie supprimée logiquement libère son nom : on peut la
            # recréer, et la synchronisation propage les deux événements.
            models.UniqueConstraint(
                fields=["shop", "name"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_category_name_per_shop_live",
            )
        ]

    def __str__(self):
        return self.name


class Product(SoftDeleteMixin, models.Model):
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
        constraints = [
            # Une référence est unique parmi les produits vivants de la boutique.
            models.UniqueConstraint(
                fields=["shop", "sku"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_sku_per_shop_live",
            ),
            # Un code-barres est unique dans une boutique, mais facultatif :
            # sans condition, plusieurs produits sans code seraient refusés.
            models.UniqueConstraint(
                fields=["shop", "barcode"],
                condition=~Q(barcode="") & Q(deleted_at__isnull=True),
                name="uniq_barcode_per_shop_live",
            ),
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


class Notification(SoftDeleteMixin, models.Model):
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


class StockMovement(SoftDeleteMixin, models.Model):
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


# ---------------------------------------------------------------------------
# Finances : dépenses manuelles saisies par le propriétaire.
# ---------------------------------------------------------------------------
class Expense(SoftDeleteMixin, models.Model):
    """Une dépense de la boutique (loyer, transport, salaire...)."""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="expenses",
                             verbose_name="Boutique")
    label = models.CharField("Libellé", max_length=120)
    amount = models.DecimalField("Montant", max_digits=12, decimal_places=2)
    category = models.CharField("Catégorie", max_length=20, choices=EXPENSE_CATEGORIES, default="autre")
    spent_at = models.DateField("Date de la dépense")
    note = models.CharField("Note", max_length=200, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_at", "-id"]
        verbose_name_plural = "dépenses"

    def __str__(self):
        return f"{self.label} — {self.amount}"


# ---------------------------------------------------------------------------
# Clients, factures et livraisons.
# ---------------------------------------------------------------------------
class Customer(SoftDeleteMixin, models.Model):
    """Un acheteur de la boutique, relié facultativement à un compte.

    Le nom peut rester anonyme : la facture fonctionne aussi sans client.
    """

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="customers",
                             verbose_name="Boutique")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name="Compte lié")
    name = models.CharField("Nom du client", max_length=150)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    address = models.CharField("Adresse de livraison", max_length=200, blank=True)
    note = models.CharField("Note", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "client"

    def __str__(self):
        return self.name or "(client anonyme)"

    @property
    def total_spent(self):
        """Total des achats du client, cumul de ses factures."""
        total = self.invoices.aggregate(
            t=Sum(
                F("lines__quantity") * F("lines__unit_price"),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        )["t"]
        return total or Decimal("0")

    @property
    def free_delivery(self):
        """Livraison offerte quand le cumul d'achats atteint le seuil de la boutique."""
        threshold = self.shop.delivery_free_threshold
        return bool(threshold and self.total_spent >= threshold)


class Invoice(SoftDeleteMixin, models.Model):
    """Facture : les produits achetés sortent du stock en mouvements OUT.

    Même sans client (achat anonyme), la facture existe et son total
    alimente la Finance via les mouvements de sortie.
    """

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="invoices",
                             verbose_name="Boutique")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="invoices", verbose_name="Client")
    reference = models.CharField("Référence", max_length=20, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name="Vendeur")
    note = models.CharField("Note", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "facture"

    def __str__(self):
        return self.reference or f"Facture #{self.pk}"

    @property
    def total(self):
        total = self.lines.aggregate(
            t=Sum(
                F("quantity") * F("unit_price"),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        )["t"]
        return total or Decimal("0")

    def save(self, *args, **kwargs):
        if not self.reference:
            n = Invoice.objects.filter(shop=self.shop).count() + 1
            while Invoice.objects.filter(shop=self.shop, reference=f"FAC-{n:04d}").exists():
                n += 1
            self.reference = f"FAC-{n:04d}"
        super().save(*args, **kwargs)


class InvoiceLine(SoftDeleteMixin, models.Model):
    """Une ligne de facture : produit, quantité et prix payé au moment de la vente."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines",
                                verbose_name="Facture")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="invoice_lines",
                                verbose_name="Produit")
    quantity = models.PositiveIntegerField("Quantité")
    unit_price = models.DecimalField("Prix unitaire", max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class DeliveryZone(SoftDeleteMixin, models.Model):
    """Zone de livraison (arrondissement/département) avec tarif associé."""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="delivery_zones",
                             verbose_name="Boutique")
    name = models.CharField("Nom de la zone", max_length=120)
    fee = models.DecimalField("Prix de livraison", max_digits=12, decimal_places=2, default=0)
    is_manual = models.BooleanField("Montant saisi manuellement", default=False,
                                    help_text="Pour les livraisons hors Brazzaville, le prix est saisi à la main.")

    class Meta:
        ordering = ["name"]
        verbose_name = "zone de livraison"
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "name"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_delivery_zone_name_per_shop_live",
            )
        ]

    def __str__(self):
        return self.name


class Delivery(SoftDeleteMixin, models.Model):
    """Une livraison : à qui, où, quand, pour quel prix et son état.

    Le prix par défaut vient des paramètres de la boutique. Si le client a
    atteint le seuil de dépense cumulée, la livraison est offerte (≈ 0).
    """

    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (PENDING, "En attente"),
        (DELIVERED, "Livrée"),
        (CANCELLED, "Annulée"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="deliveries",
                             verbose_name="Boutique")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="deliveries", verbose_name="Client")
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name="deliveries", verbose_name="Facture liée")
    zone = models.ForeignKey(DeliveryZone, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="deliveries", verbose_name="Zone de livraison")
    movement = models.ForeignKey("StockMovement", null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="deliveries", verbose_name="Sortie liée")
    address = models.CharField("Lieu de livraison", max_length=200)
    scheduled_for = models.DateField("Date de livraison", null=True, blank=True)
    fee = models.DecimalField("Prix de la livraison", max_digits=12, decimal_places=2)
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default=PENDING)
    note = models.CharField("Note", max_length=200, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "livraison"

    def __str__(self):
        target = self.customer.name if self.customer else self.address
        return f"Livraison {target} — {self.get_status_display()}"

    @property
    def is_paid(self):
        return self.fee == 0 and self.status == self.DELIVERED


def compute_delivery_fee(shop, customer):
    """Prix d'une livraison : offerte si le client a atteint le seuil, sinon le tarif par défaut."""
    if customer is not None and customer.free_delivery:
        return Decimal("0")
    return shop.delivery_fee or Decimal("0")


def get_default_delivery_zones():
    """Zones par défaut : 9 arrondissements de Brazzaville + Hors Brazzaville."""
    return [
        ("Makélékélé (1er)", Decimal("2000")),
        ("Bacongo (2e)", Decimal("2000")),
        ("Poto-Poto (3e)", Decimal("2000")),
        ("Moungali (4e)", Decimal("2000")),
        ("Ouenzé (5e)", Decimal("2000")),
        ("Talangaï (6e)", Decimal("2000")),
        ("Mfilou (7e)", Decimal("2000")),
        ("Madibou (8e)", Decimal("2000")),
        ("Djiri (9e)", Decimal("2000")),
        ("Hors Brazzaville", Decimal("0")),
    ]


def ensure_default_delivery_zones(shop):
    """Crée les zones par défaut si la boutique n'en a aucune."""
    if shop.delivery_zones.count() > 0:
        return
    for name, fee in get_default_delivery_zones():
        DeliveryZone.objects.create(
            shop=shop,
            name=name,
            fee=fee,
            is_manual=(name == "Hors Brazzaville"),
        )
