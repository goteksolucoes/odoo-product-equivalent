from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductEquivalentGroup(models.Model):
    _name = "product.equivalent.group"
    _description = "Product Equivalent Group"
    _order = "name, id"

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        help="Leave empty to make the equivalence group available to all companies.",
    )
    product_tmpl_ids = fields.One2many(
        "product.template",
        "equivalent_group_id",
        string="Equivalent Products",
    )
    note = fields.Text()

    @api.constrains("company_id", "product_tmpl_ids")
    def _check_member_companies(self):
        # This elevated existence check is limited to relational integrity. It
        # must include archived members and members hidden by record rules, but
        # it never returns their IDs or names to the caller.
        ProductTemplate = self.env["product.template"].sudo().with_context(
            active_test=False
        )
        for group in self.filtered("company_id"):
            has_incompatible_member = ProductTemplate.search_count([
                ("equivalent_group_id", "=", group.id),
                "|",
                ("company_id", "=", False),
                ("company_id", "!=", group.company_id.id),
            ], limit=1)
            if has_incompatible_member:
                raise ValidationError(_(
                    "The group's company must match every member product's company. "
                    "Use a shared group for products from different companies."
                ))
