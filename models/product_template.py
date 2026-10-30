from odoo import _, api, Command, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

from .product_product import _search_relevance


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100, name_get_uid=None):
        # Core delegates to variants, then reorders templates with its _order.
        # Rank after that final step, before applying the autocomplete limit.
        rank_results = (
            bool(name)
            and operator not in expression.NEGATIVE_TERM_OPERATORS
            and not any(term[0] == "id" for term in (args or []))
        )
        candidate_limit = max(limit, 50) if limit and rank_results else limit
        candidate_ids = list(super()._name_search(
            name, args=args, operator=operator, limit=candidate_limit,
            name_get_uid=name_get_uid,
        ))
        if not rank_results:
            return candidate_ids
        ranking_model = self.with_user(name_get_uid) if name_get_uid else self
        relevance = {
            row["id"]: _search_relevance(row, name)
            for row in ranking_model.browse(candidate_ids).read(
                ["default_code", "name"]
            )
        }
        # Python's stable sort preserves the core order for equal relevance.
        candidate_ids.sort(
            key=lambda template_id: relevance.get(template_id, (5, 0, 0))
        )
        return candidate_ids[:limit] if limit else candidate_ids

    equivalent_group_id = fields.Many2one(
        "product.equivalent.group",
        string="Equivalent Product Group",
        index=True,
        check_company=True,
        readonly=True,
        help=(
            "Legacy grouping retained for migration and audit only. "
            "It no longer drives product search."
        ),
    )
    equivalent_product_tmpl_ids = fields.One2many(
        related="equivalent_group_id.product_tmpl_ids",
        string="Legacy Equivalent Products",
        readonly=True,
        compute_sudo=False,
    )
    direct_equivalent_product_tmpl_ids = fields.Many2many(
        "product.template",
        "product_template_direct_equivalent_rel",
        "source_product_tmpl_id",
        "target_product_tmpl_id",
        string="Equivalent Products",
        copy=False,
        help=(
            "Direct commercial substitutes. The relation is symmetric but not "
            "transitive: linking A to B does not make A equivalent to B's other "
            "equivalents."
        ),
    )
    direct_equivalent_source_product_tmpl_ids = fields.Many2many(
        "product.template",
        "product_template_direct_equivalent_rel",
        "target_product_tmpl_id",
        "source_product_tmpl_id",
        string="Direct Equivalent Sources",
        copy=False,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any("direct_equivalent_product_tmpl_ids" in vals for vals in vals_list):
            records._sync_direct_equivalent_relations({record.id: set() for record in records})
        return records

    def write(self, vals):
        if "direct_equivalent_product_tmpl_ids" not in vals:
            return super().write(vals)

        previous_ids = self._direct_equivalent_id_map()
        result = super().write(vals)
        self._sync_direct_equivalent_relations(previous_ids)
        return result

    def _direct_equivalent_id_map(self):
        """Return complete edge sets for integrity bookkeeping only.

        The elevated read is deliberately narrow: it includes archived products
        and relations hidden by record rules so a permitted operation cannot
        leave a one-way edge. The result is used only to identify the inverse
        edge; that inverse write still runs as the current user and exposes no
        product data.
        """
        CompleteProductTemplate = self.env["product.template"].sudo().with_context(
            active_test=False
        )
        return {
            record.id: set(CompleteProductTemplate.search([
                ("direct_equivalent_source_product_tmpl_ids", "in", record.id),
            ]).ids)
            for record in self
        }

    def _write_inverse_direct_equivalent_commands(self, commands):
        """Write an inverse edge through core ORM checks, bypassing only this override."""
        return super().write({"direct_equivalent_product_tmpl_ids": commands})

    def _sync_direct_equivalent_relations(self, previous_ids):
        current_ids = self._direct_equivalent_id_map()
        ProductTemplate = self.env["product.template"].with_context(active_test=False)
        for template in self:
            before = previous_ids.get(template.id, set())
            after = current_ids.get(template.id, set())
            for equivalent_id in before - after:
                ProductTemplate.browse(
                    equivalent_id
                )._write_inverse_direct_equivalent_commands([
                    Command.unlink(template.id),
                ])
            for equivalent_id in after - before:
                ProductTemplate.browse(
                    equivalent_id
                )._write_inverse_direct_equivalent_commands([
                    Command.link(template.id),
                ])

    @api.constrains("company_id", "direct_equivalent_product_tmpl_ids")
    def _check_direct_equivalent_integrity(self):
        CompleteProductTemplate = self.env["product.template"].sudo().with_context(
            active_test=False
        )
        for template in self:
            has_self_link = CompleteProductTemplate.search_count([
                ("id", "=", template.id),
                ("direct_equivalent_source_product_tmpl_ids", "in", template.id),
            ], limit=1)
            if has_self_link:
                raise ValidationError(_(
                    "A product cannot be equivalent to itself."
                ))
            has_incompatible_company = template.company_id and (
                CompleteProductTemplate.search_count([
                    (
                        "direct_equivalent_source_product_tmpl_ids",
                        "in",
                        template.id,
                    ),
                    ("company_id", "!=", False),
                    ("company_id", "!=", template.company_id.id),
                ], limit=1)
            )
            if has_incompatible_company:
                raise ValidationError(_(
                    "Equivalent products must belong to the same company, or at "
                    "least one of them must be shared."
                ))

    @api.constrains("equivalent_group_id", "company_id")
    def _check_equivalent_group_company(self):
        # Preserve the company integrity of legacy rows during transition.
        for template in self:
            group = template.equivalent_group_id
            if group.company_id and group.company_id != template.company_id:
                raise ValidationError(_(
                    "The equivalence group must be shared or belong to the product's company."
                ))
