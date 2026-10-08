# SYNC.md — Protocole de synchronisation

Client Flutter ↔ API Django. Le serveur reste la référence ; le client ne lit et
n'écrit jamais en direct sur le réseau pour une opération métier.

## 1. Principes

1. **Base locale d'abord.** Toutes les lectures passent par Drift (SQLite).
   Toutes les écritures sont appliquées localement **puis** ajoutées à une file
   « outbox » persistante, dans la même transaction. Rien n'attend le réseau.
2. **Le stock n'est jamais écrasé.** Le client envoie des mouvements
   (`IN` / `OUT`), jamais une quantité absolue. Le serveur recalcule avec
   `record_movement()`, la référence unique du stock.
3. **Le réseau ne bloque jamais l'interface.** La synchronisation tourne en
   arrière-plan ; un échec est rejoué avec un recul exponentiel.
4. **Aucune saisie hors ligne n'est perdue silencieusement.** Toute opération
   refusée est conservée dans l'outbox avec une raison lisible, et l'écran
   « Synchronisation » permet de la corriger, la réessayer ou l'abandonner.

## 2. Champs ajoutés aux modèles

`uuid` (unique, fourni par le client), `updated_at`, `deleted_at` sur
`Product`, `Category`, `StockMovement`, `Notification`. `Shop`, `Membership` et
`Profile` reçoivent également `uuid` et `updated_at` (le thème doit se
synchroniser ; `Profile` a déjà `updated_at`).

- Le `uuid` est **généré par le client** : il identifie la ligne avant même
  qu'elle existe côté serveur. Si le client ne le fournit pas, le serveur en
  génère un.
- `updated_at` est maintenu automatiquement ; le pull compare `updated_at` au
  curseur.
- `deleted_at` rend la suppression logique : la ligne disparaît des listes mais
  reste visible par le pull, ce qui permet aux autres appareils de la retirer.

Migration : `0009_sync_fields`. Un `RunPython` remplit les `uuid` des lignes
existantes (`uuid.uuid4()`), sans toucher aux données.

## 3. Curseur de synchronisation

Le curseur est **opaque** pour le client (une seule chaîne à stocker) et
répond à la forme :

```json
{
  "v": 1,
  "e": {
    "shop":       {"ts": "2026-10-05T08:12:00.000Z", "id": 3},
    "category":   {"ts": "2026-10-05T08:12:00.000Z", "id": 11},
    "product":    {"ts": "2026-10-05T08:12:31.412Z", "id": 42},
    "movement":   {"ts": "2026-10-05T08:12:31.412Z", "id": 780},
    "notification": {"ts": "2026-10-05T08:09:00.000Z", "id": 9},
    "membership": {"ts": "2026-10-05T07:00:00.000Z", "id": 2},
    "profile":    {"ts": "2026-10-05T07:00:00.000Z", "id": 2}
  }
}
```

Deux choix, tous deux délibérés :

- **Une marque par entité** plutôt qu'un curseur unique : les entités sont
  modifiées indépendamment, un curseur unique forcerait à re-télécharger toute
  l'historique d'une entité dès qu'une autre change.
- **Le couple `(updated_at, id)`** plutôt que le seul `updated_at` : deux lignes
  peuvent partager la même seconde d'horodatage (enregistrement en lot,
  import, résolution d'horloge). Sans le `id` comme départage, la ligne suivante
  du tri serait sautée à la page suivante, ou répétée. La sélection est un
  `WHERE (updated_at, id) > (ts, id) ORDER BY updated_at, id`.

Chaque réponse renvoie le nouveau curseur, que le client ne persiste qu'après
avoir écrit le lot en base locale.

- `GET /api/v1/sync/pull/` **sans** `cursor` = téléchargement initial complet.
- Avec `cursor` = incrémental strict.
- Curseur illisible ou d'une version inconnue → `400` avec un message
  explicite : le client doit repartir d'un téléchargement initial plutôt que de
  deviner.

`pull` renvoie toujours les lignes **strictement postérieures** à la marque de
chaque entité, **y compris les suppressions logiques** (`deleted_at`
renseigné). Champ par entité :

```json
{
  "cursor": "<opaque>",
  "has_more": false,
  "truncated": {"shop": false, "category": false, "product": true,
                "movement": true, "notification": false,
                "membership": false, "profile": false},
  "counts": {"shop": 0, "category": 3, "product": 12, "movement": 40,
             "notification": 6, "membership": 0, "profile": 0},
  "shop":       {...},
  "categories": [...],
  "products":   [...],
  "movements":  [...],
  "notifications": [...],
  "memberships":[...],
  "profile":    {...},
  "server_time": "2026-10-05T08:12:31.412Z"
}
```

Lot maximum : **500 lignes par entité et par appel** (`?limit=` permet de
réduire ce plafond, jamais de l'augmenter ; valeur illisible ou hors bornes →
500). Au-delà, l'entité concernée est marquée `true` dans `truncated`,
`has_more` passe à `true` et le client rappelle immédiatement avec le curseur
renvoyé. **Seules les entités tronquées sont vidées** : les autres sont déjà
complètes.

`shop` et `profile` sont des objets (une seule ligne chacun) ou `null` quand la
boutique n'a pas changé depuis le curseur ; les autres sont des listes, éventuellement
vides.

Le `pull` est **en lecture seule** : il ne modifie jamais le stock.

## 4. Push

`POST /api/v1/sync/push/`

```json
{
  "device_id": "uuid-de-l-appareil",
  "operations": [
    {
      "op_id": "uuid-unique-de-l-operation",
      "type": "create",
      "entity": "product",
      "uuid": "uuid-de-la-ligne",
      "payload": { "...": "champs modifiés" },
      "client_time": "2026-10-05T08:10:00.000Z"
    }
  ]
}
```

Réponse, **par opération, dans l'ordre d'envoi** :

```json
{
  "results": [
    {
      "op_id": "…",
      "status": "applied",
      "entity": "product",
      "uuid": "…",
      "server": { "...": "état serveur après application" },
      "warning": null
    },
    {
      "op_id": "…",
      "status": "applied_with_warning",
      "warning": "Stock ramené à 0 : la sortie de 5 unités a dépassé le stock disponible (3).",
      "adjustment": { "kind": "OUT", "requested": 5, "applied": 3 },
      "server": { "...": "…" }
    },
    {
      "op_id": "…",
      "status": "rejected",
      "reason_code": "duplicate_barcode",
      "reason": "Le code-barres 6194000000015 est déjà attribué à un autre produit de cette boutique.",
      "suggestion": { "field": "barcode", "action": "choose_other" }
    }
  ],
  "cursor": "<opaque>",
  "server_time": "…"
}
```

### 4.1 Types et entités

| `type` | Entités | Effet |
| --- | --- | --- |
| `create` | `category`, `product`, `shop`, `membership`, `profile` | Création |
| `update` | `category`, `product`, `shop`, `membership`, `profile` | Mise à jour |
| `delete` | `category`, `product`, `membership` | Suppression logique |
| `movement` | `movement` | `record_movement()` — le **seul** moyen de modifier le stock |
| `adjust` | `movement` | `record_adjustment()` (écart) |
| `notification_read` | `notification` | `is_read = True` |
| `notification_read_all` | `notification` | Toutes les non lues |
| `notification_clear` | `notification` | Suppression logique de toutes les notifications |
| `photo` | `profile`, `shop` | Envoyé **en dernier**, après les données |

Un `update` ou `delete` dont la ligne n'existe pas est **rejeté**
(`not_found`), jamais créé implicitement : cela masquerait une perte de données.

### 4.2 Bornes du lot

| Cas | Réponse |
| --- | --- |
| `operations` absent ou **vide** | `400` — un lot vide est un bug du client, pas une synchronisation réussie : répondre `200` ferait disparaître des opérations de la file |
| **plus de 200 opérations** | `400` avec `reason_code: "batch_too_large"` et `suggestion: {"action": "retry"}` |

200 opérations par push : au-delà, la réponse devient ingérable pour l'app. Le
client découpe sa file et renvoie plusieurs lots.

Le lot est traité **entièrement ou pas du tout** pour une opération donnée :
chaque opération est atomique, mais une opération rejetée n'annule pas les
autres — son statut est `rejected` et les suivantes s'appliquent.

### 4.3 Idempotence

Chaque `op_id` est enregistré dans `SyncOperation` avec le résultat renvoyé.
L'unicité est **`(user, op_id)`** et non `op_id` seul : deux boutiques
différentes doivent pouvoir émettre la même opération, et un `op_id` global
ferait échouer le push de l'un sous le rejet de l'autre.

Rejouer le même `op_id` pour le même utilisateur :

- ne modifie rien en base ;
- renvoie **exactement** le même résultat (statut, raison, état serveur).

C'est ce qui rend la file sûre en cas de réponse perdue : le client peut
rejouer le lot entier sans double mouvement de stock. Le test
`test_push_is_idempotent` vérifie que deux envois du même `op_id` ne créent
qu'un seul mouvement et renvoient le même `server.quantity`.

### 4.4 Champ par champ et « dernier à écrire gagne »

Produits, catégories et thème sont fusionnés **champ par champ** quand c'est
possible :

- si `updated_at` de la ligne serveur est **strictement postérieur** à
  `client_time` de l'opération, le serveur gagne pour les champs modifiés et la
  réponse porte `warning` (« Champs non appliqués : X a été modifié entre-temps
  sur un autre appareil. ») ;
- sinon l'opération s'applique, et le champ serveur garde la valeur la plus
  récente.

Le stock, lui, n'entre jamais dans cette fusion : il est toujours recalculé à
partir des mouvements.

## 5. Règles de conflit

| # | Règle | Comportement serveur | `status` |
| --- | --- | --- | --- |
| 1 | **Le stock n'est jamais écrasé** | `payload.quantity` est **ignoré** sur `create` et `update` de produit. Seul `type: "movement"` change le stock. Un ajustement manuel hors ligne est converti en mouvement de différence : un `adjust` avec `previous_quantity` et `quantity` devient `record_adjustment()` ; si le serveur a bougé entre-temps, le serveur calcule l'écart par rapport à son propre état et renvoie `applied_with_warning` en exposant le calcul. | `applied` |
| 2 | **Dernier à écrire gagne, champ par champ** | Voir § 4.4. | `applied` ou `applied_with_warning` |
| 3 | **Sortie rendant le stock négatif** | Appliquer la sortie jusqu'à `0` (`record_movement()` puis correction), créer une notification `ADJ` expliquant la correction, renvoyer `adjustment` avec `requested` / `applied`. | `applied_with_warning` |
| 4 | **Produit supprimé en ligne, mouvements hors ligne en attente** | Le mouvement est rejeté avec `reason_code: "product_deleted"`, `reason: "« X » a été supprimé le … ; ce mouvement n'a pas pu être enregistré."`, `suggestion.action: "discard_or_create"`. Les autres opérations du lot ne sont pas affectées. | `rejected` |
| 5 | **Unicité barcode / sku / nom de catégorie** | Doublon → `rejected` avec `reason_code` et le champ fautif dans `suggestion.field`, message reprenant celui du formulaire web. | `rejected` |

Règle 4 en détail : « supprimé en ligne » signifie `deleted_at` renseigné côté
serveur **et** le curseur du client antérieur à cette suppression. Si le client
a déjà vu la suppression (son pull est à jour) et envoie quand même, la raison
indique que la suppression est connue — plus-actionnable que « produit
introuvable ».

## 6. Raisons de rejet (codes stables + messages français)

| `reason_code` | Message |
| --- | --- |
| `not_found` | « Cette ligne n'existe pas sur le serveur. » |
| `product_deleted` | « Le produit a été supprimé sur un autre appareil. » |
| `permission_denied` | « Vous n'avez pas la permission de modifier cette donnée. » |
| `duplicate_barcode` | « Le code-barres X est déjà attribué à un autre produit de cette boutique. » |
| `duplicate_sku` | « Cette référence existe déjà. » |
| `duplicate_category` | « Cette catégorie existe déjà. » |
| `invalid_field` | « Champ « X » : <message du formulaire web>. » |
| `invalid_quantity` | « La quantité doit être au moins 1. » |
| `negative_quantity` | « La quantité ne peut pas être négative. » |
| `invalid_kind` | « Type de mouvement invalide : utilisez "IN" ou "OUT". » |
| `bad_payload` | « Contenu de l'opération illisible. » |
| `batch_too_large` | « Lot trop volumineux : 200 opérations maximum. » |
| `scanner_disabled` | « Le scanner est désactivé pour cette boutique. » |
| `image_too_heavy` | « Photo trop lourde (2 Mo maximum). » |
| `image_invalid` | « Fichier image invalide. » |

Le client affiche `reason` tel quel et propose l'action correspondant à
`suggestion.action` : `choose_other` (corriger le champ), `retry` (réessayer),
`discard_or_create` (abandonner ou recréer), `contact_owner`.

## 7. Photos et logo

Photos de profil et logo sont envoyés **en dernier** :

1. le client enfile d'abord toutes les opérations de données ;
2. une fois l'outbox de données vide (ou au moment prévu), il envoie
   `type: "photo"` en `multipart/form-data`, avec le fichier ;
3. le serveur valide avec `clean_image_upload()` — mêmes règles que le web
   (2 Mo, JPEG/PNG/WebP/GIF pour le profil ; ouverture Pillow).

Le `multipart` est un appel séparé : `POST /api/v1/sync/push/photo/`. Cela évite
qu'un fichier binaire échoue et fasse perdre le lot de données déjà envoyé.

## 8. Sécurité et Journalisation

| Mesure | Valeur |
| --- | --- |
| Lot maximal par `push` | 200 opérations (`batch_too_large` au-delà) |
| Lot maximal par `pull` | 500 lignes par entité |
| Limitation de débit | 60 requêtes/minute par utilisateur sur `push`, 120/minute sur `pull` (`throttle_classes`) |
| Validation | `max_length` sur toutes les chaînes, choix fermés pour `kind` / `level`, UUID validé, payload non-dict rejeté |
| Journalisation des rejets | `SyncOperation(status="rejected", reason_code, reason, payload)` conservé ; l'app expose l'historique |
| Suppression du journal | 30 jours après traitement (tâche de nettoyage) |
| Isolation | Toute opération est vérifiée contre la boutique du `Membership` de l'utilisateur avant d'être appliquée |

## 9. Boucle de synchronisation côté client

```
démarrage de l'app ─┐
retour au premier plan
toutes les N minutes
« Synchroniser maintenant »
retour d'internet détecté
                     │
                     ▼
   connectivity_plus dit « connecté » ?
                     │ non → état « Hors ligne », on attend
                     ▼ oui
   test d'accès réel au serveur (HEAD /sync/status/, 5 s)
                     │ échec → état « Hors ligne », backoff
                     ▼ succès
   état « Synchronisation… »
                     │
   ┌─────────────────┴──────────────────┐
   ▼                                     ▼
push(outbox par lots de 100)        pull(cursor)
   │                                     │
   ├ applied / applied_with_warning  → retiré de l'outbox, toast si warning
   ├ rejected (définitif)           → conservé, badge « rejetée », action requise
   └ erreur réseau                  → backoff exponentiel 5 s → 30 s → 2 min → 5 min (plafond)
                     │
                     ▼
   état « En ligne » ou « N opérations en attente »
```

Backoff : `min(2^tentative × 5 s, 5 min)`, remis à zéro après un tour complet
réussi. Sur mobile, `workmanager` déclenche un cycle au minimum toutes les
15 minutes ; le cycle respecte le même ordre (push puis pull) et n'exige pas de
session au premier plan.

**Au retour au premier plan**, l'application force un cycle et joue le bip des
nouvelles notifications reçues pendant l'absence (au plus 5 bips, 700 ms
d'écart, comme le web).

## 10. Ordre de résolution d'un produit

Pour que le stock displayed hors ligne soit cohérent, l'application applique
les opérations dans cet ordre au push :

1. `create` / `update` de catégorie (une catégorie doit exister avant un produit) ;
2. `create` de produit ;
3. `movement` (stock) ;
4. `update` de produit (champs éditoriaux) ;
5. `delete` (produit, puis catégorie) ;
6. `photo` / `logo`.

L'outbox stocke un `seq` monotone ; le tri par `seq` garantit cet ordre.

Côté serveur, `payload.product` accepte quatre formes, résolues dans cet ordre
par `api.serializers.resolve_product()` :

1. `uuid` de la ligne ;
2. **code-barres** — espace ins ignoré ;
3. identifiant numérique, si la valeur n'est un code connu d'aucun produit ;
4. `sku` (référence).

Le code-barres passe **avant** l'identifiant parce qu'un code à 8 chiffres ou
plus serait sinon lu comme un `pk` : la sortie irait sur le mauvais produit.
Le nom n'est jamais accepté — deux produits peuvent porter le même nom, et une
sortie de stock ne doit pas se tromper de cible.

Les catégories suivent la même idée (`api.serializers.CategoryRefField`) :
`uuid`, identifiant, puis nom insensible à la casse. Une catégorie inconnue ou
appartenant à une autre boutique est un rejet, jamais une création implicite.

Toutes ces résolutions sont **cloisonnées par boutique** : une référence
d'une autre boutique est traitée comme introuvable.

## 11. Cas de figure traités par les tests d'intégration

| Scénario | Attendu |
| --- | --- |
| Produit et deux mouvements créés hors ligne, application relancée | Base locale intacte, outbox conservée (3 opérations) |
| Retour d'internet | `push` applique, `pull` renvoie le même état, stock identique au local |
| Sortie plus grande que le stock hors ligne | `applied_with_warning`, stock ramené à 0, notification `ADJ` présente |
| Suppression d'un produit sur un autre appareil pendant qu'il est en attente | Mouvement `rejected` avec `product_deleted`, visible dans l'écran Synchronisation |
| Doublon de code-barres créé hors ligne | `rejected` avec `duplicate_barcode`, champ `barcode` proposé à la correction |
| Relecture du même lot | Résultats identiques, aucun mouvement en double |