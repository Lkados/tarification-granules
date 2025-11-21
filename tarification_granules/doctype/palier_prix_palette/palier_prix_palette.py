"""Controller for Palier Prix Palette DocType (Child Table)."""

import frappe
from frappe import _
from frappe.model.document import Document


class PalierPrixPalette(Document):
    """Palier de prix pour tarification par quantité (table enfant)."""

    def validate(self) -> None:
        """Validation du palier.

        Génère automatiquement la description et vérifie la cohérence.

        Raises:
            frappe.ValidationError: Si validation échoue
        """
        # Vérifier qte_min <= qte_max si défini
        if self.qte_max and self.qte_min > self.qte_max:
            frappe.throw(
                _("La quantité minimum ne peut pas être supérieure à la quantité maximum"),
                exc=frappe.ValidationError
            )

        # Générer description automatiquement
        self._generate_description()

    def _generate_description(self) -> None:
        """Génère la description du palier."""
        if self.qte_max:
            self.description = f"{self.qte_min}-{self.qte_max} palettes"
        else:
            self.description = f"{self.qte_min}+ palettes"
