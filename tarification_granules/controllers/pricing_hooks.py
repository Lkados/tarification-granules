"""
Hooks de tarification automatique pour Sales Order et Sales Invoice.

Ce module applique automatiquement les tarifs configurés sur les palettes
de granulés lors de la validation des commandes et factures.
"""

from typing import Optional

import frappe
from frappe import _

from tarification_granules.api.tarif_calculator import (
    calculate_prix_palette,
    is_palette_article,
)


def apply_pricing(doc, method: Optional[str] = None) -> None:
    """Applique automatiquement les tarifs sur Sales Order et Sales Invoice.

    Logique d'application :
    - Sales Order : Toujours recalculer les prix
    - Sales Invoice créée depuis SO : Prix déjà corrects, skip
    - Sales Invoice directe : Recalculer les prix

    Args:
        doc: Document Sales Order ou Sales Invoice
        method: Nom de la méthode appelante (before_validate, etc.)

    Returns:
        None (modifie le document en place)
    """
    if not doc.customer:
        return

    # Si Sales Invoice créée depuis Sales Order, ne pas recalculer
    if doc.doctype == "Sales Invoice" and _is_from_sales_order(doc):
        frappe.msgprint(
            _("Prix hérités de la commande client, pas de recalcul."),
            indicator="blue",
            alert=True,
        )
        return

    # Récupérer la zone du client
    customer_doc = frappe.get_cached_doc("Customer", doc.customer)
    zone = customer_doc.territory

    if not zone:
        frappe.msgprint(
            _("⚠️ Client sans zone assignée. Tarification non appliquée."),
            indicator="orange",
            alert=True,
        )
        return

    # Appliquer les tarifs sur les lignes
    items_updated = _apply_pricing_to_items(doc, zone)

    # Message de confirmation
    if items_updated > 0:
        _show_success_message(doc.doctype, items_updated, zone)


def _is_from_sales_order(doc) -> bool:
    """Vérifie si la Sales Invoice est créée depuis une Sales Order.

    Args:
        doc: Document Sales Invoice

    Returns:
        True si créée depuis SO, False sinon
    """
    if not doc.items:
        return False

    return any(item.sales_order for item in doc.items)


def _apply_pricing_to_items(doc, zone: str) -> int:
    """Applique les tarifs sur les lignes de palettes.

    Args:
        doc: Document Sales Order ou Sales Invoice
        zone: Zone tarifaire du client

    Returns:
        Nombre de lignes tarifées
    """
    items_updated = 0
    date_ref = doc.get("transaction_date") or doc.get("posting_date")

    for item in doc.items:
        if not is_palette_article(item.item_code):
            continue

        try:
            pricing = calculate_prix_palette(
                customer=doc.customer,
                article_palette=item.item_code,
                quantite=int(item.qty),
                date_reference=date_ref,
            )

            # Appliquer le prix calculé
            item.rate = pricing["prix_final"]
            item.custom_prix_base = pricing["prix_base"]
            item.custom_remise_appliquee = pricing["remise"]
            item.custom_zone_tarif = pricing["zone"]
            item.custom_tarif_id = pricing.get("tarif_id")

            items_updated += 1

        except frappe.ValidationError as e:
            frappe.msgprint(
                _("❌ Erreur tarification {0}: {1}").format(item.item_code, str(e)),
                indicator="red",
                alert=True,
            )

    return items_updated


def _show_success_message(doctype: str, items_count: int, zone: str) -> None:
    """Affiche un message de succès après tarification.

    Args:
        doctype: Type de document (Sales Order ou Sales Invoice)
        items_count: Nombre de lignes tarifées
        zone: Zone tarifaire appliquée

    Returns:
        None
    """
    doc_type_label = _("commande") if doctype == "Sales Order" else _("facture")

    frappe.msgprint(
        _(
            "✅ {0} ligne(s) de palette tarifée(s) automatiquement pour la {1} (Zone: {2})"
        ).format(items_count, doc_type_label, zone),
        indicator="green",
        alert=True,
    )
