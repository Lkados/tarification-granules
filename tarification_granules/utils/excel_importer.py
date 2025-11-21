"""
Utilitaire d'import des tarifs depuis fichier Excel.

Ce module permet d'importer les tarifs de palettes depuis le fichier
Zones.xlsx contenant les zones géographiques et leurs frais de livraison.
"""

from typing import Dict, List
import openpyxl
import frappe
from frappe import _


@frappe.whitelist()
def import_tarifs_from_zones_excel(
    file_path: str,
    article_palette: str = "PALETTE-GRANULES",
    prix_base: float = 405.0,
    methode: str = "Prix de base + Remise quantité"
) -> Dict:
    """Importe les tarifs depuis le fichier Zones.xlsx.

    Format attendu du fichier Excel :
    | CP | COMMUNE | ZONE | FRAIS DE LIVRAISON |

    Génère un Tarif Palette par zone unique avec :
    - Prix = prix_base + frais_livraison_moyen

    Args:
        file_path: Chemin vers le fichier Excel
        article_palette: Code de l'article (défaut: PALETTE-GRANULES)
        prix_base: Prix de base avant frais de livraison (défaut: 405€)
        methode: Méthode de tarification (défaut: Prix de base + Remise)

    Returns:
        Dictionnaire avec :
        - created (int): Nombre de tarifs créés
        - updated (int): Nombre de tarifs mis à jour
        - errors (List[str]): Liste des erreurs rencontrées
        - zones (List[str]): Liste des zones traitées

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        frappe.ValidationError: Si le format du fichier est invalide

    Example:
        >>> import_tarifs_from_zones_excel("/path/to/Zones.xlsx")
        {
            "created": 22,
            "updated": 0,
            "errors": [],
            "zones": ["ZONE 1", "ZONE 2", ...]
        }
    """
    # Vérifier que le fichier existe
    try:
        wb = openpyxl.load_workbook(file_path)
    except FileNotFoundError:
        frappe.throw(_("Fichier non trouvé : {0}").format(file_path))

    ws = wb.active

    # Collecter les zones uniques avec leurs frais moyens
    zones_frais = _collect_zones_from_excel(ws)

    # Créer/mettre à jour les tarifs
    result = _create_tarifs_from_zones(
        zones_frais,
        article_palette,
        prix_base,
        methode
    )

    frappe.db.commit()

    return result


def _collect_zones_from_excel(worksheet) -> Dict[str, List[float]]:
    """Collecte les zones et leurs frais de livraison depuis Excel.

    Args:
        worksheet: Feuille Excel openpyxl

    Returns:
        Dictionnaire {zone: [liste des frais]}
    """
    zones_frais = {}

    for i, row in enumerate(worksheet.iter_rows(values_only=True)):
        # Skip headers (2 premières lignes)
        if i <= 1:
            continue

        if not row[2]:  # ZONE requis
            continue

        zone = str(row[2]).strip()

        # Gérer les cas spéciaux pour les frais
        if not row[3] or str(row[3]).upper() in ["PAS DE LIVRAISON", "N/A", ""]:
            frais = 0.0
        else:
            try:
                frais = float(row[3])
            except (ValueError, TypeError):
                frais = 0.0

        if zone not in zones_frais:
            zones_frais[zone] = []
        zones_frais[zone].append(frais)

    return zones_frais


def _create_tarifs_from_zones(
    zones_frais: Dict[str, List[float]],
    article_palette: str,
    prix_base: float,
    methode: str
) -> Dict:
    """Crée ou met à jour les tarifs pour chaque zone.

    Args:
        zones_frais: Dictionnaire {zone: [liste des frais]}
        article_palette: Code de l'article
        prix_base: Prix de base
        methode: Méthode de tarification

    Returns:
        Dictionnaire avec statistiques d'import
    """
    created = 0
    updated = 0
    errors = []
    zones_list = []

    for zone, frais_list in zones_frais.items():
        try:
            frais_moyen = sum(frais_list) / len(frais_list)
            prix_final = prix_base + frais_moyen

            # Chercher un tarif existant pour cette zone (indépendamment de l'article)
            existing = frappe.db.exists("Tarif Palette", {
                "zone": zone,
                "actif": 1
            })

            if existing:
                # Tarif existe pour cette zone
                tarif_doc = frappe.get_doc("Tarif Palette", existing)

                # Chercher si l'article existe déjà dans la child table
                article_found = False
                for article_row in tarif_doc.articles:
                    if article_row.article_palette == article_palette:
                        # Mettre à jour la ligne existante
                        article_row.prix_base_ht = prix_final
                        article_row.frais_livraison = frais_moyen
                        article_found = True
                        break

                if not article_found:
                    # Ajouter une nouvelle ligne article
                    tarif_doc.append("articles", {
                        "article_palette": article_palette,
                        "prix_base_ht": prix_final,
                        "frais_livraison": frais_moyen,
                        "utiliser_remises_globales": 1
                    })

                tarif_doc.save(ignore_permissions=True)
                updated += 1
            else:
                # Créer nouveau tarif avec l'article dans la child table
                tarif_doc = frappe.get_doc({
                    "doctype": "Tarif Palette",
                    "zone": zone,
                    "methode_tarification": methode,
                    "date_debut": frappe.utils.today(),
                    "actif": 1,
                    "articles": [{
                        "article_palette": article_palette,
                        "prix_base_ht": prix_final,
                        "frais_livraison": frais_moyen,
                        "utiliser_remises_globales": 1
                    }]
                })
                tarif_doc.insert(ignore_permissions=True)
                created += 1

            zones_list.append(zone)

        except Exception as e:
            errors.append(f"{zone}: {str(e)}")
            frappe.log_error(
                title=_("Erreur import tarif {0}").format(zone),
                message=str(e)
            )

    return {
        "created": created,
        "updated": updated,
        "errors": errors,
        "zones": zones_list
    }


@frappe.whitelist()
def get_import_status(file_path: str) -> Dict:
    """Prévisualise l'import sans créer les tarifs.

    Args:
        file_path: Chemin vers le fichier Excel

    Returns:
        Statistiques de l'import potentiel
    """
    try:
        wb = openpyxl.load_workbook(file_path)
    except FileNotFoundError:
        frappe.throw(_("Fichier non trouvé : {0}").format(file_path))

    ws = wb.active
    zones_frais = _collect_zones_from_excel(ws)

    return {
        "total_zones": len(zones_frais),
        "zones": list(zones_frais.keys()),
        "preview": {
            zone: {
                "count": len(frais),
                "frais_moyen": sum(frais) / len(frais)
            }
            for zone, frais in zones_frais.items()
        }
    }
