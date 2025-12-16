"""Configuration des custom fields pour Sales Order et Sales Invoice.

Ce module crée les champs personnalisés permettant d'afficher les détails
de la tarification automatique sur les lignes de commande et de facture.
"""

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import \
    create_custom_fields


def setup_custom_fields() -> None:
    """Crée les custom fields pour Sales Order Item et Sales Invoice Item.

    Crée les champs suivants sur les deux DocTypes :
    - Section de tarification (collapsible)
    - Prix de base HT
    - Remise quantité appliquée
    - Zone tarifaire
    - ID du tarif appliqué

    Returns:
        None
    """
    custom_fields = _get_custom_fields_definition()
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()

    frappe.logger().info("Custom fields créés pour tarification_granules")


def _get_custom_fields_definition() -> dict:
    """Retourne la définition des custom fields.

    Returns:
        Dictionnaire avec la structure des custom fields
    """
    fields_definition = [
        {
            "fieldname": "custom_tarif_section",
            "label": _("Tarification Automatique"),
            "fieldtype": "Section Break",
            "insert_after": "rate",
            "collapsible": 1,
        },
        {
            "fieldname": "custom_prix_base",
            "label": _("Prix Base HT"),
            "fieldtype": "Currency",
            "insert_after": "custom_tarif_section",
            "read_only": 1,
            "in_list_view": 0,
            "options": "currency",
            "description": _("Prix de base avant remise quantité"),
        },
        {
            "fieldname": "custom_remise_appliquee",
            "label": _("Remise Quantité"),
            "fieldtype": "Currency",
            "insert_after": "custom_prix_base",
            "read_only": 1,
            "in_list_view": 0,
            "options": "currency",
            "description": _("Montant de la remise appliquée"),
        },
        {
            "fieldname": "custom_col_break_tarif",
            "fieldtype": "Column Break",
            "insert_after": "custom_remise_appliquee",
        },
        {
            "fieldname": "custom_zone_tarif",
            "label": _("Zone Tarifaire"),
            "fieldtype": "Data",
            "insert_after": "custom_col_break_tarif",
            "read_only": 1,
            "in_list_view": 0,
            "description": _("Zone géographique du client"),
        },
        {
            "fieldname": "custom_tarif_id",
            "label": _("Tarif Appliqué"),
            "fieldtype": "Link",
            "options": "Tarif Palette",
            "insert_after": "custom_zone_tarif",
            "read_only": 1,
            "in_list_view": 0,
            "description": _("Référence du tarif utilisé"),
        },
    ]

    return {
        "Sales Order Item": fields_definition,
        "Sales Invoice Item": fields_definition,
    }
