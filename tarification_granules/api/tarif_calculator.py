"""Module de calcul automatique des tarifs de palettes.

Ce module fournit les fonctions de calcul de prix selon la zone du client
et la quantité commandée, avec support de deux méthodes de tarification.
"""

from typing import Dict, Optional

import frappe
from frappe import _


@frappe.whitelist()
def calculate_prix_palette(
    customer: str,
    article_palette: str,
    quantite: int = 1,
    date_reference: Optional[str] = None,
) -> Dict:
    """Calcule le prix final d'une palette selon la méthode configurée.

    Args:
        customer: ID du client
        article_palette: Code de l'article palette
        quantite: Quantité commandée
        date_reference: Date de référence (défaut: aujourd'hui)

    Returns:
        Dictionnaire avec:
        - prix_base: Prix de base HT
        - remise: Montant de la remise
        - prix_final: Prix final après remise
        - zone: Zone tarifaire du client
        - methode: Méthode de tarification utilisée
        - details: Détails du calcul
        - tarif_id: ID du tarif appliqué

    Example:
        >>> calculate_prix_palette("CUST-001", "PALETTE-GRANULES", 5)
        {
            "prix_base": 410.0,
            "remise": 15.0,
            "prix_final": 395.0,
            "zone": "ZONE 1",
            "methode": "Prix de base + Remise quantité",
            "details": "Remise 4+ palettes",
            "tarif_id": "TAR-2025-0001"
        }
    """
    if not date_reference:
        date_reference = frappe.utils.today()

    # Récupérer la zone du client
    zone = frappe.db.get_value("Customer", customer, "territory")
    if not zone:
        frappe.throw(_("Le client {0} n'a pas de zone assignée").format(customer))

    # Chercher le tarif actif pour cette zone et cet article
    tarif = _get_tarif_actif(zone, article_palette, date_reference)
    if not tarif:
        frappe.throw(
            _("Aucun tarif actif trouvé pour la zone {0} et l'article {1}").format(
                zone, article_palette
            )
        )

    # Calculer selon la méthode
    if tarif.methode_tarification == "Prix de base + Remise quantité":
        return _calculate_prix_avec_remise(tarif, quantite, zone)
    else:
        return _calculate_prix_par_palier(tarif, quantite, zone)


def _get_tarif_actif(
    zone: str, article_palette: str, date_reference: str
) -> Optional[frappe._dict]:
    """Récupère le tarif actif pour une zone et un article.

    Args:
        zone: Zone géographique
        article_palette: Code article
        date_reference: Date de référence

    Returns:
        Tuple (Document Tarif Palette, row article) ou None
    """
    filters = {"zone": zone, "actif": 1, "date_debut": ["<=", date_reference]}

    # Chercher tous les tarifs actifs pour cette zone
    tarifs = frappe.get_all(
        "Tarif Palette",
        filters=filters,
        fields=["name", "methode_tarification", "date_debut", "date_fin"],
        order_by="date_debut desc",
    )

    # Pour chaque tarif, chercher l'article dans la child table
    for tarif_row in tarifs:
        if not tarif_row.date_fin or tarif_row.date_fin >= date_reference:
            tarif_doc = frappe.get_doc("Tarif Palette", tarif_row.name)

            # Chercher l'article dans la child table
            for article_row in tarif_doc.articles:
                if article_row.article_palette == article_palette:
                    # Attacher la row article au document pour faciliter l'accès
                    tarif_doc._article_row = article_row
                    return tarif_doc

    return None


def _calculate_prix_avec_remise(tarif: frappe._dict, quantite: int, zone: str) -> Dict:
    """Calcule le prix avec méthode base + remise.

    Args:
        tarif: Document Tarif Palette (avec _article_row attaché)
        quantite: Quantité
        zone: Zone tarifaire

    Returns:
        Dictionnaire avec détails du calcul
    """
    article_row = tarif._article_row
    prix_base = article_row.prix_base_ht
    remise = 0.0
    details = ""

    # Appliquer remise quantité si activée pour cet article
    if article_row.utiliser_remises_globales:
        regle = _get_regle_remise(quantite)
        if regle:
            remise = regle.remise_montant
            details = regle.nom_regle

    prix_final = prix_base - remise

    return {
        "prix_base": prix_base,
        "remise": remise,
        "prix_final": prix_final,
        "zone": zone,
        "methode": "Prix de base + Remise quantité",
        "details": details,
        "tarif_id": tarif.name,
        "article": article_row.article_palette,
    }


def _calculate_prix_par_palier(tarif: frappe._dict, quantite: int, zone: str) -> Dict:
    """Calcule le prix avec méthode par paliers.

    Args:
        tarif: Document Tarif Palette
        quantite: Quantité
        zone: Zone tarifaire

    Returns:
        Dictionnaire avec détails du calcul
    """
    if not tarif.paliers_prix:
        frappe.throw(_("Aucun palier de prix défini pour ce tarif"))

    # Trouver le palier correspondant
    palier = None
    for p in tarif.paliers_prix:
        if p.qte_min <= quantite:
            if not p.qte_max or quantite <= p.qte_max:
                palier = p
                break

    if not palier:
        # Prendre le dernier palier par défaut
        palier = tarif.paliers_prix[-1]

    return {
        "prix_base": palier.prix_unitaire_ht,
        "remise": 0.0,
        "prix_final": palier.prix_unitaire_ht,
        "zone": zone,
        "methode": "Prix direct par palier",
        "details": palier.description or f"{palier.qte_min}+ palettes",
        "tarif_id": tarif.name,
    }


def _get_regle_remise(quantite: int) -> Optional[frappe._dict]:
    """Récupère la règle de remise applicable.

    Args:
        quantite: Quantité commandée

    Returns:
        Document Regle Remise Quantite ou None
    """
    regles = frappe.get_all(
        "Regle Remise Quantite",
        filters={"actif": 1},
        fields=[
            "name",
            "nom_regle",
            "qte_min",
            "qte_max",
            "remise_montant",
            "priorite",
        ],
        order_by="priorite desc",
    )

    for regle in regles:
        if regle.qte_min <= quantite:
            if not regle.qte_max or quantite <= regle.qte_max:
                return regle

    return None


@frappe.whitelist()
def is_palette_article(item_code: str) -> bool:
    """Vérifie si un article est une palette de granulés.

    Args:
        item_code: Code de l'article

    Returns:
        True si l'article est une palette
    """
    if not item_code:
        return False

    item_code_upper = item_code.upper()
    return "PALETTE" in item_code_upper or "GRANULE" in item_code_upper
