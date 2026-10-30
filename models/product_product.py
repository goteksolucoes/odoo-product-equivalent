from difflib import SequenceMatcher
import re

from odoo import api, models
from odoo.fields import Domain


def _search_relevance(product, query):
    """Rank a candidate by how closely its code/name matches the typed text."""
    query = (query or "").strip().casefold()
    if not query:
        return (5, 0, 0)

    code = (product.get("default_code") or "").casefold()
    name = (product.get("name") or "").casefold()
    values = (code, name)
    if query in values:
        return (0, 0, 0)

    prefix_positions = [value.find(query) for value in values if value.startswith(query)]
    if prefix_positions:
        prefix_lengths = [len(value) for value in values if value.startswith(query)]
        return (1, min(prefix_positions), min(prefix_lengths))

    tokens = [token for value in values for token in re.split(r"\W+", value) if token]
    if query in tokens:
        return (2, 0, 0)

    positions = [value.find(query) for value in values if query in value]
    if positions:
        return (3, min(positions), min(len(value) for value in values if query in value))

    similarity = max(
        (SequenceMatcher(None, query, value).ratio() for value in values if value),
        default=0,
    )
    return (4, -similarity, 0)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    @api.readonly
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        product_ids = self._name_search(
            name=name,
            domain=domain,
            operator=operator,
            limit=limit,
        )
        return [
            (product.id, product.display_name)
            for product in self.browse(product_ids).sudo()
        ]

    @api.model
    def _name_search(
        self,
        name="",
        args=None,
        operator="ilike",
        limit=100,
        name_get_uid=None,
        domain=None,
    ):
        """Extend native product lookup with manually-defined commercial equivalents.

        Design goals:
        - keep Odoo's native product search as the source of truth;
        - preserve domains received from callers (sale_ok, company, etc.);
        - only expand positive searches;
        - append equivalents without duplicating the native results.
        """
        base_domain = list(domain if domain is not None else (args or []))
        # Odoo's native SQL order favors populated default_code values over
        # NULL codes. Keep a bounded candidate window, then rank by text match.
        positive_search = operator not in Domain.NEGATIVE_OPERATORS
        normalized_limit = limit if limit else None
        search_limit = (
            max(normalized_limit, 50)
            if normalized_limit and positive_search and name
            else normalized_limit
        )
        native_pairs = super().name_search(
            name=name,
            domain=base_domain,
            operator=operator,
            limit=search_limit,
        )
        native_ids = [product_id for product_id, _ in native_pairs]

        if not name or not positive_search or not native_ids:
            return native_ids

        anchor_template_ids = self.env["product.template"].search(
            [("product_variant_ids", "in", native_ids)],
        ).ids
        equivalent_ids = []
        if anchor_template_ids:
            equivalent_template_ids = self.env["product.template"].search(
                [
                    (
                        "direct_equivalent_product_tmpl_ids",
                        "in",
                        anchor_template_ids,
                    ),
                ],
            ).ids
            if equivalent_template_ids:
                equivalent_domain = Domain(base_domain) & Domain([
                    ("product_tmpl_id", "in", equivalent_template_ids),
                    ("id", "not in", native_ids),
                ])
                equivalent_ids = self.search(
                    equivalent_domain,
                    limit=search_limit,
                    order=self._order,
                ).ids

        candidate_ids = native_ids + equivalent_ids
        candidate_data = self.browse(candidate_ids).read(
            ["default_code", "name"]
        )
        relevance = {
            row["id"]: _search_relevance(row, name)
            for row in candidate_data
        }
        native_id_set = set(native_ids)
        original_order = {
            product_id: index for index, product_id in enumerate(candidate_ids)
        }
        candidate_ids.sort(
            key=lambda product_id: (
                relevance.get(product_id, (5, 0, 0)),
                0 if product_id in native_id_set else 1,
                original_order[product_id],
            )
        )
        return candidate_ids[:normalized_limit] if normalized_limit else candidate_ids
