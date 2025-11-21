# 💰 Tarification Granulés

Application ERPNext 15 pour la gestion automatique des tarifs de palettes de granulés par zone géographique avec remises quantitatives.

## 🎯 Fonctionnalités

- ✅ Tarification automatique sur **Sales Order** et **Sales Invoice**
- ✅ Deux méthodes de tarification au choix :
  - Méthode 1 : Prix de base + Remise quantité
  - Méthode 2 : Prix direct par palier de quantité
- ✅ 22 zones géographiques avec frais de livraison
- ✅ Import automatique depuis Excel (Zones.xlsx)
- ✅ Custom fields pour traçabilité complète
- ✅ 100% conforme standards ERPNext 15

---

## 📋 PRÉREQUIS

1. **ERPNext 15** installé et fonctionnel
2. **App josseaume_energies** (pour attribution automatique des zones aux clients)
3. **Python 3.10+**
4. **Fichier Zones.xlsx** avec vos 575 communes

---

## 🚀 INSTALLATION

### Étape 1 : L'app est déjà créée ✅

L'app a été générée et installée sur votre site.

### Étape 2 : Créer les DocTypes

Vous devez créer **3 DocTypes** via l'interface ERPNext :

#### A. DocType "Regle Remise Quantite"

```
Setup → DocType → New

Nom: Regle Remise Quantite
Naming: field:nom_regle

Champs:
1. nom_regle (Data, Unique, Requis) - "Nom de la règle"
2. qte_min (Int, Requis) - "Quantité minimum"
3. qte_max (Int) - "Quantité maximum (vide = et plus)"
4. remise_montant (Currency, Requis) - "Montant de la remise (€)"
5. actif (Check, Default=1) - "Actif"
6. priorite (Int, Default=0) - "Priorité"
```

#### B. DocType "Palier Prix Palette" (Table enfant)

```
Setup → DocType → New

Nom: Palier Prix Palette
Is Child Table: ✓

Champs:
1. qte_min (Int, Requis, In List View) - "Quantité Min"
2. qte_max (Int, In List View) - "Quantité Max"
3. prix_unitaire_ht (Currency, Requis, In List View) - "Prix Unitaire HT"
4. description (Data, Read Only, In List View) - "Description"
```

#### C. DocType "Tarif Palette"

```
Setup → DocType → New

Nom: Tarif Palette
Naming: TAR-.YYYY.-.####

Champs (dans l'ordre):

[Section: Identification]
1. zone (Link → Territory, Requis, In List View)
2. article_palette (Link → Item, Requis, In List View)

[Section: Méthode de Tarification]
3. methode_tarification (Select, Requis, Default="Prix de base + Remise quantité")
   Options:
   - Prix de base + Remise quantité
   - Prix direct par palier

[Section: Prix de Base (Méthode 1)]
   Depends On: eval:doc.methode_tarification=='Prix de base + Remise quantité'
4. prix_base_ht (Currency, Mandatory Depends On: eval:doc.methode_tarification=='Prix de base + Remise quantité')
5. frais_livraison (Currency, Read Only)
6. [Column Break]
7. utiliser_remises_globales (Check, Default=1)

[Section: Paliers de Prix (Méthode 2)]
   Depends On: eval:doc.methode_tarification=='Prix direct par palier'
8. paliers_prix (Table → Palier Prix Palette)

[Section: Période de Validité]
9. date_debut (Date, Requis, Default=Today)
10. date_fin (Date)
11. [Column Break]
12. actif (Check, Default=1)

[Section: Notes (Collapsible)]
13. notes (Small Text)
```

### Étape 3 : Installer les Custom Fields

```bash
cd /Users/mohamedkachtit/Desktop/frappe-bench
bench --site erpnext.local console
```

Dans la console Python :

```python
from tarification_granules.setup.custom_fields import setup_custom_fields
setup_custom_fields()
exit()
```

### Étape 4 : Importer les règles de remise par défaut

Via console :

```bash
bench --site erpnext.local console
```

```python
import frappe

# Créer règle 1
frappe.get_doc({
    "doctype": "Regle Remise Quantite",
    "nom_regle": "Remise 2-3 palettes",
    "qte_min": 2,
    "qte_max": 3,
    "remise_montant": 5.0,
    "actif": 1
}).insert()

# Créer règle 2
frappe.get_doc({
    "doctype": "Regle Remise Quantite",
    "nom_regle": "Remise 4+ palettes",
    "qte_min": 4,
    "remise_montant": 15.0,
    "actif": 1
}).insert()

frappe.db.commit()
exit()
```

### Étape 5 : Importer vos 22 zones depuis Excel

```bash
bench --site erpnext.local console
```

```python
from tarification_granules.utils.excel_importer import import_tarifs_from_zones_excel

result = import_tarifs_from_zones_excel(
    file_path="/Users/mohamedkachtit/Desktop/frappe-bench/apps/copie a suivre/Zones.xlsx",
    article_palette="PALETTE-GRANULES",
    prix_base=405.0,
    methode="Prix de base + Remise quantité"
)

print(f"✅ {result['created']} tarifs créés")
print(f"✅ {result['updated']} tarifs mis à jour")
print(f"Zones: {result['zones']}")

exit()
```

### Étape 6 : Redémarrer le serveur

```bash
bench restart
```

---

## 📊 UTILISATION

### Scénario 1 : Sales Order avec tarification automatique

1. Créer un nouveau **Sales Order**
2. Sélectionner un **Client** (qui doit avoir une zone assignée via josseaume_energies)
3. Ajouter une ligne : **PALETTE-GRANULES** × 5
4. **Automatiquement** :
   - Prix calculé : 395€ (410€ - 15€ de remise)
   - Custom fields remplis :
     - Prix Base HT : 410€
     - Remise Quantité : 15€
     - Zone Tarifaire : ZONE 1
     - Tarif Appliqué : TAR-2025-0001

### Scénario 2 : Sales Invoice directe

Même fonctionnement que Sales Order.

### Scénario 3 : Sales Invoice depuis Sales Order

- Prix **hérités** automatiquement de la SO
- **Pas de recalcul** (message affiché)

---

## 🔧 CONFIGURATION AVANCÉE

### Créer un tarif avec prix par palier (Méthode 2)

1. Aller dans **Tarif Palette** → New
2. Remplir :
   - Zone : ZONE 2
   - Article Palette : PALETTE-GRANULES
   - Méthode de Calcul : **Prix direct par palier**
3. Dans la table **Paliers de Prix** :

```
┌─────────┬─────────┬──────────────────┐
│ Qté Min │ Qté Max │ Prix Unitaire HT │
├─────────┼─────────┼──────────────────┤
│    1    │    1    │      425€        │
│    2    │    3    │      420€        │
│    4    │    5    │      415€        │
│    6    │  (vide) │      410€        │
└─────────┴─────────┴──────────────────┘
```

4. Sauvegarder

---

## 📁 STRUCTURE DU PROJET

```
tarification_granules/
├── tarification_granules/
│   ├── api/
│   │   └── tarif_calculator.py       # ⭐ Logique de calcul des prix
│   ├── hooks/
│   │   └── pricing_hooks.py          # ⭐ Hooks SO et SI
│   ├── setup/
│   │   └── custom_fields.py          # Configuration custom fields
│   ├── utils/
│   │   └── excel_importer.py         # Import depuis Excel
│   ├── fixtures/
│   │   └── regle_remise_quantite.json # Règles par défaut
│   └── hooks.py                       # ⭐ Configuration centrale
└── README.md
```

---

## 🐛 DÉPANNAGE

### Erreur "Module not found"

```bash
bench restart
```

### Custom fields non visibles

```bash
bench --site erpnext.local clear-cache
bench restart
```

### Prix non appliqués automatiquement

Vérifier :

1. Le client a bien une zone assignée (champ `territory`)
2. Un tarif existe pour cette zone + article
3. Le tarif est actif et dans la période de validité
4. L'article est bien identifié comme palette (contient "PALETTE" ou "GRANULE")

---

## 📚 API DOCUMENTATION

### Fonctions whitelisted disponibles

```python
# Calculer le prix d'une palette
calculate_prix_palette(customer, article_palette, quantite, date_reference)

# Importer tarifs depuis Excel
import_tarifs_from_zones_excel(file_path, article_palette, prix_base, methode)

# Prévisualiser import
get_import_status(file_path)

# Vérifier si article est une palette
is_palette_article(item_code)
```

---

## ✅ CHECKLIST POST-INSTALLATION

- [ ] 3 DocTypes créés (Tarif Palette, Palier Prix Palette, Regle Remise Quantite)
- [ ] Custom fields installés sur Sales Order Item et Sales Invoice Item
- [ ] 2 règles de remise créées
- [ ] 22 tarifs importés depuis Excel
- [ ] Test : créer une SO → prix appliqué automatiquement
- [ ] Test : créer une SI directe → prix appliqué
- [ ] Test : créer SI depuis SO → prix hérités

---

## 🤝 SUPPORT

Créé par : **Mohamed Kachtit** (mokachtit@gmail.com)

Développé selon les standards ERPNext 15 et les best practices Frappe.

## 📝 LICENSE

MIT License
