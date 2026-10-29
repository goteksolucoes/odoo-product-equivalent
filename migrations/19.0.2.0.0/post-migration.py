from odoo import _, api, Command, SUPERUSER_ID
from odoo.exceptions import UserError


def _active_group_pairs(env):
    ProductTemplate = env["product.template"].with_context(active_test=False)
    for group in env["product.equivalent.group"].search([
        ("active", "=", True),
    ]):
        members = ProductTemplate.search([
            ("equivalent_group_id", "=", group.id),
        ])
        if len(members) > 2:
            raise UserError(_(
                "Cannot migrate active equivalence group '%(group)s' (ID %(id)s): "
                "it has %(count)s members.",
                group=group.display_name,
                id=group.id,
                count=len(members),
            ))
        if len(members) == 2:
            company_ids = {company_id for company_id in members.mapped("company_id").ids}
            if len(company_ids) > 1:
                raise UserError(_(
                    "Cannot migrate active equivalence group '%(group)s' (ID %(id)s): "
                    "its two products belong to different specific companies.",
                    group=group.display_name,
                    id=group.id,
                ))
            yield group, members


def migrate(cr, installed_version):
    del installed_version
    env = api.Environment(cr, SUPERUSER_ID, {"active_test": False})
    for group, members in _active_group_pairs(env):
        first, second = members
        if second not in first.direct_equivalent_product_tmpl_ids:
            first.write({
                "direct_equivalent_product_tmpl_ids": [Command.link(second.id)],
            })
        if first not in second.direct_equivalent_product_tmpl_ids:
            second.write({
                "direct_equivalent_product_tmpl_ids": [Command.link(first.id)],
            })
        # Mark the legacy source as migrated so a later script rerun cannot
        # recreate a direct link that a user intentionally removed.
        group = env["product.equivalent.group"].browse(group.id)
        group.write({"active": False})
