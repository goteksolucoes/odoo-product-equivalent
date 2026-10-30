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
        - keep Odoo's native product search as the source of truth;
        - preserve domains received from callers (sale_ok, company, etc.);
        - only expand positive searches;
        - append equivalents without duplicating the native results.
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

        if name and operator not in expression.NEGATIVE_TERM_OPERATORS and native_ids:
            ranking_model = self.with_user(name_get_uid) if name_get_uid else self
            native_data = ranking_model.browse(native_ids).read(["default_code", "name"])
            relevance = {
                row["id"]: _search_relevance(row, name)
                for row in native_data
            }
            original_order = {
                product_id: index for index, product_id in enumerate(native_ids)
            }
            native_ids.sort(
                key=lambda product_id: (
                    relevance.get(product_id, (5, 0, 0)),
                    original_order[product_id],
                )
            )
            if limit:
                native_ids = native_ids[:limit]

        if not name or operator in expression.NEGATIVE_TERM_OPERATORS or not native_ids:
            return native_ids

        if limit and len(native_ids) >= limit:
            return native_ids

        anchor_template_ids = list(
            self.env["product.template"]._search(
                [("product_variant_ids", "in", native_ids)],
                access_rights_uid=name_get_uid,
            )
        )
        if not anchor_template_ids:
            return native_ids

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
        if not equivalent_template_ids:
            return native_ids

        remaining = (limit - len(native_ids)) if limit else False
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
                limit=remaining,
                access_rights_uid=name_get_uid,
            )
        )
        if equivalent_ids:
            ranking_model = self.with_user(name_get_uid) if name_get_uid else self
            equivalent_data = ranking_model.browse(equivalent_ids).read(
                ["default_code", "name"]
            )
            relevance = {
                row["id"]: _search_relevance(row, name)
                for row in equivalent_data
            }
            original_order = {
                product_id: index for index, product_id in enumerate(equivalent_ids)
            }
            equivalent_ids.sort(
                key=lambda product_id: (
                    relevance.get(product_id, (5, 0, 0)),
                    original_order[product_id],
                )
            )
        return native_ids + equivalent_ids
