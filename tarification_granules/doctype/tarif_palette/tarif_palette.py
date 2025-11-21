"""Controller for Tarif Palette DocType."""

import frappe
from frappe import _
from frappe.model.document import Document
from typing import Optional


class TarifPalette(Document):
    """Tarif de palette par zone avec deux méthodes de calcul possibles."""

    def validate(self) -> None:
        """Validation du tarif.

        Vérifie la cohérence des champs selon la méthode choisie.

        Raises:
            frappe.ValidationError: Si validation échoue
        """
        self._validate_method_fields()
        self._validate_date_range()
        self._validate_paliers()

    def _validate_method_fields(self) -> None:
        """Vérifie que les champs requis sont remplis selon la méthode."""
        if self.methode_tarification == "Prix de base + Remise quantité":
            if not self.prix_base_ht:
                frappe.throw(
                    _("Le prix de base HT est requis pour la méthode 'Prix de base + Remise quantité'"),
                    exc=frappe.ValidationError
                )
        elif self.methode_tarification == "Prix direct par palier":
            if not self.paliers_prix or len(self.paliers_prix) == 0:
                frappe.throw(
                    _("Au moins un palier de prix est requis pour la méthode 'Prix direct par palier'"),
                    exc=frappe.ValidationError
                )

    def _validate_date_range(self) -> None:
        """Vérifie que date_fin >= date_debut si renseignée."""
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            frappe.throw(
                _("La date de fin ne peut pas être antérieure à la date de début"),
                exc=frappe.ValidationError
            )

    def _validate_paliers(self) -> None:
        """Vérifie la cohérence des paliers de prix."""
        if self.methode_tarification != "Prix direct par palier":
            return

        if not self.paliers_prix:
            return

        # Vérifier qu'il n'y a pas de chevauchements
        paliers = sorted(self.paliers_prix, key=lambda p: p.qte_min)

        for i, palier in enumerate(paliers):
            # Vérifier cohérence min/max
            if palier.qte_max and palier.qte_min > palier.qte_max:
                frappe.throw(
                    _("Palier ligne {0}: La quantité min ne peut pas être supérieure à la quantité max").format(i + 1),
                    exc=frappe.ValidationError
                )

            # Vérifier pas de chevauchement avec le suivant
            if i < len(paliers) - 1:
                next_palier = paliers[i + 1]
                if palier.qte_max and palier.qte_max >= next_palier.qte_min:
                    frappe.throw(
                        _(
                            "Chevauchement détecté entre les paliers lignes {0} et {1}"
                        ).format(i + 1, i + 2),
                        exc=frappe.ValidationError
                    )

    def before_save(self) -> None:
        """Actions avant sauvegarde."""
        # Si la zone a un frais de livraison défini dans Territory, le récupérer
        if self.zone and self.methode_tarification == "Prix de base + Remise quantité":
            self._update_frais_livraison()

    def _update_frais_livraison(self) -> None:
        """Met à jour les frais de livraison depuis la zone si disponible.

        Note: Cette fonction est un placeholder. Les frais de livraison
        sont normalement calculés lors de l'import Excel.
        """
        # Les frais de livraison sont déjà définis lors de l'import Excel
        # Cette méthode peut être étendue si nécessaire
        pass
