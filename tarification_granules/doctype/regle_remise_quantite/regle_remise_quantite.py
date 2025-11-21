"""Controller for Regle Remise Quantite DocType."""

import frappe
from frappe import _
from frappe.model.document import Document


class RegleRemiseQuantite(Document):
    """Règle de remise quantitative pour les palettes."""

    def validate(self) -> None:
        """Validation du document.

        Vérifie que qte_min <= qte_max si qte_max est renseignée.

        Raises:
            frappe.ValidationError: Si validation échoue
        """
        if self.qte_max and self.qte_min > self.qte_max:
            frappe.throw(
                _("La quantité minimum ne peut pas être supérieure à la quantité maximum"),
                exc=frappe.ValidationError
            )

        # Vérifier qu'il n'existe pas déjà une règle qui couvre exactement les mêmes quantités
        if not self.is_new():
            return

        filters = {
            "name": ["!=", self.name],
            "actif": 1,
            "qte_min": self.qte_min
        }

        if self.qte_max:
            filters["qte_max"] = self.qte_max
        else:
            filters["qte_max"] = ["is", "not set"]

        existing = frappe.db.exists("Regle Remise Quantite", filters)

        if existing:
            frappe.throw(
                _("Une règle existe déjà pour cette plage de quantités"),
                exc=frappe.ValidationError
            )
