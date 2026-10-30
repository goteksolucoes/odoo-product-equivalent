from difflib import SequenceMatcher
import re

from odoo import api, models
from odoo.osv import expression


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
    def _name_search(self, name, args=None, operator="ilike", limit=100, name_get_uid=None):
        """Extend native product lookup with manually-defined commercial equivalents.

        Design goals:
        - keep Odoo's native product search as the source of candidate anchors;
        - preserve domains received from callers (sale_ok, company, etc.);
        - only expand positive searches;
        - rank native matches and direct equivalents together.
        """
        args = list(args or [])
        # Odoo's native SQL order favors populated default_code values over
        # NULL codes. Keep a bounded candidate window, then rank by text match.
        positive_search = operator not in expression.NEGATIVE_TERM_OPERATORS
        search_limit = (
            max(limit, 50)
            if limit and positive_search and name
            else limit
        )
        native_ids = list(
            super()._name_search(
                name=name,
                args=args,
                operator=operator,
                limit=search_limit,
                name_get_uid=name_get_uid,
            )
        )

        if not name or not positive_search or not native_ids:
            return native_ids

        anchor_template_ids = list(
            self.env["product.template"]._search(
                [("product_variant_ids", "in", native_ids)],
                access_rights_uid=name_get_uid,
            )
        )
        equivalent_ids = []
        if anchor_template_ids:
            equivalent_template_ids = list(
                self.env["product.template"]._search(
                    [
                        (
                            "direct_equivalent_product_tmpl_ids",
                            "in",
                            anchor_template_ids,
                        ),
                    ],
                    access_rights_uid=name_get_uid,
                )
            )
            if equivalent_template_ids:
                equivalent_domain = expression.AND([
                    args,
                    [
                        ("product_tmpl_id", "in", equivalent_template_ids),
                        ("id", "not in", native_ids),
                    ],
                ])
                equivalent_ids = list(
                    self._search(
                        equivalent_domain,
                        limit=search_limit,
                        access_rights_uid=name_get_uid,
                    )
                )

        # The autocomplete renders IDs in the order returned by _name_search.
        # Rank both sources together so a strong text match among equivalents
        # can outrank a weak native hit (for example a supplier-code match).
        candidate_ids = native_ids + equivalent_ids
        # access_rights_uid affects ACL checks in _search, not current-user rules.
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
        return candidate_ids[:limit] if limit else candidate_ids
