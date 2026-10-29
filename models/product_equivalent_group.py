from odoo import fields, models


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
