from odoo import api, models
from odoo.osv import expression


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
        native_ids = list(
            super()._name_search(
                name=name,
                args=args,
                operator=operator,
                limit=limit,
                name_get_uid=name_get_uid,
            )
        )

        if not name or operator in expression.NEGATIVE_TERM_OPERATORS or not native_ids:
            return native_ids

        if limit and len(native_ids) >= limit:
            return native_ids

        anchors = self.browse(native_ids)
        group_ids = anchors.mapped("product_tmpl_id.equivalent_group_id").ids
        if not group_ids:
            return native_ids

        remaining = (limit - len(native_ids)) if limit else False
        equivalent_domain = expression.AND([
            args,
            [
                ("product_tmpl_id.equivalent_group_id", "in", group_ids),
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
        return native_ids + equivalent_ids
