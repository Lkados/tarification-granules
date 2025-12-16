"""Script d'installation automatique de l'application tarification_granules.

Ce module gère l'installation complète et automatique de l'application :
- Création des DocTypes
- Installation des custom fields
- Import des fixtures (règles de remise par défaut)
"""

import json
import os

import frappe
from frappe import _


def after_install() -> None:
    """Hook appelé après l'installation de l'app.

    Installe tous les composants nécessaires :
    1. DocTypes (depuis JSON)
    2. Custom fields
    3. Fixtures (règles de remise)

    Returns:
        None
    """
    frappe.logger().info("🚀 Début installation tarification_granules")

    try:
        # Étape 1 : Installer les DocTypes
        _install_doctypes()

        # Étape 2 : Installer les custom fields
        _install_custom_fields()

        # Étape 3 : Importer les fixtures
        _import_fixtures()

        # Message de succès
        frappe.msgprint(
            _(
                "✅ Installation terminée avec succès !<br><br>"
                "• 3 DocTypes créés<br>"
                "• Custom fields installés<br>"
                "• 2 règles de remise importées<br><br>"
                "Prochaines étapes :<br>"
                "1. Créer un article 'PALETTE-GRANULES'<br>"
                "2. Importer vos zones depuis Excel via la console"
            ),
            title=_("Installation Tarification Granulés"),
            indicator="green",
        )

        frappe.logger().info("✅ Installation tarification_granules terminée")

    except Exception as e:
        frappe.log_error(
            title=_("Erreur installation tarification_granules"), message=str(e)
        )
        frappe.throw(
            _("Erreur lors de l'installation : {0}").format(str(e)),
            exc=frappe.ValidationError,
        )


def _install_doctypes() -> None:
    """Installe les DocTypes depuis les fichiers JSON.

    Ordre d'installation :
    1. Regle Remise Quantite (indépendant)
    2. Palier Prix Palette (child table)
    3. Tarif Palette (principal)

    Raises:
        Exception: Si erreur lors de l'installation
    """
    frappe.logger().info("📦 Installation des DocTypes...")

    doctypes_order = ["regle_remise_quantite", "palier_prix_palette", "tarif_palette"]

    for doctype_name in doctypes_order:
        _install_single_doctype(doctype_name)

    frappe.db.commit()
    frappe.logger().info("✅ DocTypes installés")


def _install_single_doctype(doctype_name: str) -> None:
    """Installe un seul DocType depuis son fichier JSON.

    Args:
        doctype_name: Nom du DocType en snake_case

    Raises:
        FileNotFoundError: Si le fichier JSON n'existe pas
        Exception: Si erreur lors de l'installation
    """
    # Construire le chemin vers le fichier JSON
    app_path = frappe.get_app_path("tarification_granules")
    json_path = os.path.join(app_path, "doctype", doctype_name, f"{doctype_name}.json")

    if not os.path.exists(json_path):
        frappe.throw(
            _("Fichier DocType introuvable : {0}").format(json_path),
            exc=FileNotFoundError,
        )

    # Charger le JSON
    with open(json_path, "r", encoding="utf-8") as f:
        doctype_data = json.load(f)

    doctype_display_name = doctype_data.get("name")

    # Vérifier si le DocType existe déjà
    if frappe.db.exists("DocType", doctype_display_name):
        frappe.logger().info(f"⏭️  DocType '{doctype_display_name}' existe déjà, skip")
        return

    # Créer le DocType
    try:
        doc = frappe.get_doc(doctype_data)
        doc.insert(ignore_permissions=True)
        frappe.logger().info(f"✅ DocType '{doctype_display_name}' créé")
    except Exception as e:
        frappe.logger().error(
            f"❌ Erreur création DocType '{doctype_display_name}': {str(e)}"
        )
        raise


def _install_custom_fields() -> None:
    """Installe les custom fields sur Sales Order Item et Sales Invoice Item.

    Utilise le module setup.custom_fields existant.

    Raises:
        Exception: Si erreur lors de l'installation
    """
    frappe.logger().info("🔧 Installation des custom fields...")

    try:
        from tarification_granules.setup.custom_fields import \
            setup_custom_fields

        setup_custom_fields()
        frappe.logger().info("✅ Custom fields installés")
    except Exception as e:
        frappe.logger().error(f"❌ Erreur installation custom fields: {str(e)}")
        raise


def _import_fixtures() -> None:
    """Importe les fixtures (règles de remise par défaut).

    Lit le fichier fixtures/regle_remise_quantite.json et crée les documents.

    Raises:
        FileNotFoundError: Si le fichier fixtures n'existe pas
        Exception: Si erreur lors de l'import
    """
    frappe.logger().info("📥 Import des fixtures...")

    # Chemin vers le fichier fixtures
    app_path = frappe.get_app_path("tarification_granules")
    fixtures_path = os.path.join(app_path, "fixtures", "regle_remise_quantite.json")

    if not os.path.exists(fixtures_path):
        frappe.logger().warning(f"⚠️  Fichier fixtures introuvable : {fixtures_path}")
        return

    # Charger les fixtures
    with open(fixtures_path, "r", encoding="utf-8") as f:
        fixtures_data = json.load(f)

    # Importer chaque règle
    for rule_data in fixtures_data:
        rule_name = rule_data.get("nom_regle")

        # Vérifier si existe déjà
        if frappe.db.exists("Regle Remise Quantite", rule_name):
            frappe.logger().info(f"⏭️  Règle '{rule_name}' existe déjà, skip")
            continue

        try:
            doc = frappe.get_doc(rule_data)
            doc.insert(ignore_permissions=True)
            frappe.logger().info(f"✅ Règle '{rule_name}' créée")
        except Exception as e:
            frappe.logger().error(f"❌ Erreur création règle '{rule_name}': {str(e)}")
            # Continue avec les autres règles même si une échoue

    frappe.db.commit()
    frappe.logger().info("✅ Fixtures importées")
