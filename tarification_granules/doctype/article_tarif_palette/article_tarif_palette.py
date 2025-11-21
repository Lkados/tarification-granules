"""DocType Article Tarif Palette - Child table des articles dans un tarif."""

from typing import TYPE_CHECKING
import frappe
from frappe import _
from frappe.model.document import Document

if TYPE_CHECKING:
    from frappe.types import DF


class ArticleTarifPalette(Document):
    """Article dans un tarif de palette."""

    # Type hints pour les champs
    if TYPE_CHECKING:
        article_palette: DF.Link
        prix_base_ht: DF.Currency
        frais_livraison: DF.Currency
        utiliser_remises_globales: DF.Check

    def validate(self) -> None:
        """Validation du document."""
        self._validate_article_exists()
        self._validate_prix_positif()

    def _validate_article_exists(self) -> None:
        """Vérifie que l'article existe."""
        if not frappe.db.exists("Item", self.article_palette):
            frappe.throw(
                _("L'article {0} n'existe pas").format(self.article_palette)
            )

    def _validate_prix_positif(self) -> None:
        """Vérifie que le prix est positif."""
        if self.prix_base_ht and self.prix_base_ht < 0:
            frappe.throw(_("Le prix de base ne peut pas être négatif"))

        if self.frais_livraison and self.frais_livraison < 0:
            frappe.throw(_("Les frais de livraison ne peuvent pas être négatifs"))
