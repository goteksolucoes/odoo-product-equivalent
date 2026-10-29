from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    equivalent_group_id = fields.Many2one(
        "product.equivalent.group",
        string="Equivalent Product Group",
        index=True,
        check_company=True,
        help=(
            "Products in the same group are commercial substitutes. "
            "Searching one of them in a sales order can also return the other products in the group."
        ),
    )
    equivalent_product_tmpl_ids = fields.One2many(
        related="equivalent_group_id.product_tmpl_ids",
        string="Equivalent Products",
        readonly=True,
    )
