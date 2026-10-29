from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestDirectEquivalentSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create({
            "name": "PEQ Security A",
            "default_code": "PEQ-DIRECT-SEC-A",
        })
        cls.product_b = cls.env["product.product"].create({
            "name": "PEQ Security B",
            "default_code": "PEQ-DIRECT-SEC-B",
        })
        cls.product_a.product_tmpl_id.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.link(cls.product_b.product_tmpl_id.id),
            ],
        })

    def _new_rule_user(
        self,
        model_name,
        domain_force,
        suffix,
        groups="base.group_user",
        rule_permissions=None,
    ):
        security_group = self.env["res.groups"].create({
            "name": "PEQ Direct Rule %s" % suffix,
        })
        user = new_test_user(
            self.env,
            login="peq_direct_%s" % suffix,
            groups=groups,
            company_id=self.env.company.id,
            company_ids=[Command.set([self.env.company.id])],
        )
        user.groups_id = [Command.link(security_group.id)]
        rule_values = {
            "name": "PEQ Direct Rule %s" % suffix,
            "model_id": self.env["ir.model"]._get(model_name).id,
            "domain_force": repr(domain_force),
            "groups": [Command.link(security_group.id)],
        }
        rule_values.update(rule_permissions or {})
        self.env["ir.rule"].create(rule_values)
        return user

    def _search_as(self, user, context=None):
        Product = self.env["product.product"].with_user(user)
        if context:
            Product = Product.with_context(**context)
        return Product._name_search(
            "PEQ-DIRECT-SEC-A",
            name_get_uid=self.env.ref("base.user_admin").id,
        )

    def test_current_template_rule_applies_with_alternate_name_get_uid(self):
        user = self._new_rule_user(
            "product.template",
            [("id", "!=", self.product_b.product_tmpl_id.id)],
            "template_neighbor",
        )

        ids = self._search_as(user)

        self.assertEqual(ids, [self.product_a.id])

    def test_anchor_template_rule_applies_with_alternate_name_get_uid(self):
        user = self._new_rule_user(
            "product.template",
            [("id", "!=", self.product_a.product_tmpl_id.id)],
            "template_anchor",
        )

        ids = self._search_as(user)

        self.assertEqual(ids, [])

    def test_current_variant_rule_applies_with_alternate_name_get_uid(self):
        user = self._new_rule_user(
            "product.product",
            [("id", "=", self.product_a.id)],
            "variant_neighbor",
        )

        ids = self._search_as(user)

        self.assertEqual(ids, [self.product_a.id])

    def test_archived_neighbor_respects_active_test(self):
        self.product_b.active = False

        default_ids = self.env["product.product"]._name_search("PEQ-DIRECT-SEC-A")
        all_ids = self.env["product.product"].with_context(
            active_test=False
        )._name_search("PEQ-DIRECT-SEC-A")

        self.assertEqual(default_ids, [self.product_a.id])
        self.assertEqual(all_ids[0], self.product_a.id)
        self.assertIn(self.product_b.id, all_ids)

    def test_inverse_write_preserves_target_record_rule(self):
        source = self.env["product.template"].create({"name": "PEQ Rule Source"})
        target = self.env["product.template"].create({"name": "PEQ Rule Target"})
        user = self._new_rule_user(
            "product.template",
            [("id", "!=", target.id)],
            "mutation_target",
            groups="sales_team.group_sale_manager,product.group_product_manager",
        )

        with self.assertRaises(AccessError), self.env.cr.savepoint():
            source.with_user(user).write({
                "direct_equivalent_product_tmpl_ids": [Command.link(target.id)],
            })
        source.invalidate_recordset(["direct_equivalent_product_tmpl_ids"])
        target.invalidate_recordset(["direct_equivalent_product_tmpl_ids"])

        self.assertNotIn(target.id, source.direct_equivalent_product_tmpl_ids.ids)
        self.assertNotIn(source.id, target.direct_equivalent_product_tmpl_ids.ids)

    def test_clear_cannot_make_hidden_existing_edge_asymmetric(self):
        source = self.env["product.template"].create({"name": "PEQ Hidden Edge Source"})
        target = self.env["product.template"].create({"name": "PEQ Hidden Edge Target"})
        source.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(target.id)],
        })
        (source | target).invalidate_recordset([
            "direct_equivalent_product_tmpl_ids",
            "direct_equivalent_source_product_tmpl_ids",
        ])
        user = self._new_rule_user(
            "product.template",
            [("id", "!=", target.id)],
            "hidden_existing_edge",
            groups="sales_team.group_sale_manager,product.group_product_manager",
        )

        source.with_user(user).write({
            "direct_equivalent_product_tmpl_ids": [Command.clear()],
        })
        (source | target).invalidate_recordset([
            "direct_equivalent_product_tmpl_ids",
            "direct_equivalent_source_product_tmpl_ids",
        ])

        self.assertIn(target.id, source.direct_equivalent_product_tmpl_ids.ids)
        self.assertIn(source.id, target.direct_equivalent_product_tmpl_ids.ids)

    def test_failed_inverse_unlink_rolls_back_both_sides(self):
        source = self.env["product.template"].create({"name": "PEQ Unlink Rule Source"})
        target = self.env["product.template"].create({"name": "PEQ Unlink Rule Target"})
        source.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(target.id)],
        })
        (source | target).invalidate_recordset([
            "direct_equivalent_product_tmpl_ids",
            "direct_equivalent_source_product_tmpl_ids",
        ])
        user = self._new_rule_user(
            "product.template",
            [("id", "!=", target.id)],
            "unlink_target",
            groups="sales_team.group_sale_manager,product.group_product_manager",
            rule_permissions={
                "perm_read": False,
                "perm_write": True,
                "perm_create": False,
                "perm_unlink": False,
            },
        )

        with self.assertRaises(AccessError), self.env.cr.savepoint():
            source.with_user(user).write({
                "direct_equivalent_product_tmpl_ids": [Command.unlink(target.id)],
            })
        (source | target).invalidate_recordset([
            "direct_equivalent_product_tmpl_ids",
            "direct_equivalent_source_product_tmpl_ids",
        ])

        self.assertIn(target.id, source.direct_equivalent_product_tmpl_ids.ids)
        self.assertIn(source.id, target.direct_equivalent_product_tmpl_ids.ids)

    def test_caller_company_domain_filters_direct_neighbor(self):
        company_b = self.env["res.company"].create({"name": "PEQ Search Company B"})
        shared_anchor = self.env["product.product"].create({
            "name": "PEQ Shared Search Anchor",
            "default_code": "PEQ-SHARED-ANCHOR",
        })
        company_b_neighbor = self.env["product.product"].create({
            "name": "PEQ Company B Search Neighbor",
            "company_id": company_b.id,
        })
        shared_anchor.product_tmpl_id.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.link(company_b_neighbor.product_tmpl_id.id),
            ],
        })

        ids = self.env["product.product"]._name_search(
            "PEQ-SHARED-ANCHOR",
            args=[
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.env.company.id),
            ],
        )

        self.assertIn(shared_anchor.id, ids)
        self.assertNotIn(company_b_neighbor.id, ids)
