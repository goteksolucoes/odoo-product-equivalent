from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestDirectEquivalentRelation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.template_a = cls.ProductTemplate.create({"name": "PEQ Direct A"})
        cls.template_b = cls.ProductTemplate.create({"name": "PEQ Direct B"})
        cls.template_c = cls.ProductTemplate.create({"name": "PEQ Direct C"})
        cls.template_d = cls.ProductTemplate.create({"name": "PEQ Direct D"})

    def _ids(self, template):
        return set(
            template.with_context(
                active_test=False
            ).direct_equivalent_product_tmpl_ids.ids
        )

    def test_create_builds_symmetric_edges(self):
        created = self.ProductTemplate.create({
            "name": "PEQ Created With Edge",
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_b.id)],
        })

        self.assertEqual(self._ids(created), {self.template_b.id})
        self.assertIn(created.id, self._ids(self.template_b))

    def test_create_multi_builds_all_inverse_edges(self):
        created = self.ProductTemplate.create([
            {
                "name": "PEQ Multi Create One",
                "direct_equivalent_product_tmpl_ids": [
                    Command.link(self.template_c.id),
                ],
            },
            {
                "name": "PEQ Multi Create Two",
                "direct_equivalent_product_tmpl_ids": [
                    Command.link(self.template_c.id),
                ],
            },
        ])

        self.assertEqual(self._ids(created[0]), {self.template_c.id})
        self.assertEqual(self._ids(created[1]), {self.template_c.id})
        self.assertTrue(set(created.ids) <= self._ids(self.template_c))

    def test_link_and_unlink_are_symmetric(self):
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_b.id)],
        })
        self.assertIn(self.template_b.id, self._ids(self.template_a))
        self.assertIn(self.template_a.id, self._ids(self.template_b))

        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.unlink(self.template_b.id)],
        })
        self.assertNotIn(self.template_b.id, self._ids(self.template_a))
        self.assertNotIn(self.template_a.id, self._ids(self.template_b))

    def test_clear_includes_archived_edges_with_active_test_false(self):
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_b.id)],
        })
        self.template_b.active = False

        self.template_a.with_context(active_test=False).write({
            "direct_equivalent_product_tmpl_ids": [Command.clear()],
        })

        self.assertFalse(self._ids(self.template_a))
        self.assertNotIn(self.template_a.id, self._ids(self.template_b))

    def test_set_and_legacy_replace_commands_update_both_sides(self):
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.set([self.template_b.id, self.template_c.id]),
            ],
        })
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.set([self.template_c.id, self.template_d.id]),
            ],
        })

        self.assertEqual(self._ids(self.template_a), {self.template_c.id, self.template_d.id})
        self.assertNotIn(self.template_a.id, self._ids(self.template_b))
        self.assertIn(self.template_a.id, self._ids(self.template_c))
        self.assertIn(self.template_a.id, self._ids(self.template_d))

        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [(6, 0, [self.template_b.id])],
        })
        self.assertEqual(self._ids(self.template_a), {self.template_b.id})
        self.assertIn(self.template_a.id, self._ids(self.template_b))
        self.assertNotIn(self.template_a.id, self._ids(self.template_c))
        self.assertNotIn(self.template_a.id, self._ids(self.template_d))

    def test_multi_record_write_builds_each_inverse_edge(self):
        (self.template_a | self.template_b).write({
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_c.id)],
        })

        self.assertIn(self.template_c.id, self._ids(self.template_a))
        self.assertIn(self.template_c.id, self._ids(self.template_b))
        self.assertTrue(
            {self.template_a.id, self.template_b.id} <= self._ids(self.template_c)
        )

    def test_copy_does_not_copy_equivalence(self):
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_b.id)],
        })

        copied = self.template_a.copy({"name": "PEQ Direct A Copy"})

        self.assertFalse(self._ids(copied))
        self.assertNotIn(copied.id, self._ids(self.template_b))

    def test_self_link_is_rejected(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.template_a.write({
                "direct_equivalent_product_tmpl_ids": [
                    Command.link(self.template_a.id),
                ],
            })

    def test_company_compatibility_allows_same_or_shared_only(self):
        company_a = self.env.company
        company_b = self.env["res.company"].create({"name": "PEQ Direct Company B"})
        specific_a = self.ProductTemplate.create({
            "name": "PEQ Specific A",
            "company_id": company_a.id,
        })
        same_company = self.ProductTemplate.create({
            "name": "PEQ Same Company",
            "company_id": company_a.id,
        })
        specific_b = self.ProductTemplate.create({
            "name": "PEQ Specific B",
            "company_id": company_b.id,
        })
        shared = self.ProductTemplate.create({"name": "PEQ Shared"})

        specific_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(same_company.id)],
        })
        shared.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.link(specific_a.id),
                Command.link(specific_b.id),
            ],
        })

        self.assertIn(same_company.id, self._ids(specific_a))
        self.assertTrue({specific_a.id, specific_b.id} <= self._ids(shared))
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            specific_a.write({
                "direct_equivalent_product_tmpl_ids": [
                    Command.link(specific_b.id),
                ],
            })

    def test_company_change_cannot_invalidate_existing_edge(self):
        company_b = self.env["res.company"].create({"name": "PEQ Change Company B"})
        self.template_a.company_id = self.env.company
        self.template_b.company_id = self.env.company
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_b.id)],
        })

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.template_b.company_id = company_b

    def test_product_unlink_relies_on_many2many_cascade(self):
        self.template_a.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(self.template_b.id)],
        })

        deleted_id = self.template_a.id
        self.template_a.unlink()
        self.template_b.invalidate_cache(["direct_equivalent_product_tmpl_ids"])

        self.assertNotIn(deleted_id, self._ids(self.template_b))


class TestDirectEquivalentSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create({
            "name": "PEQ Chain A",
            "default_code": "PEQ-DIRECT-A",
            "sale_ok": True,
        })
        cls.product_b = cls.env["product.product"].create({
            "name": "PEQ Chain B",
            "default_code": "PEQ-DIRECT-B",
            "sale_ok": True,
        })
        cls.product_c = cls.env["product.product"].create({
            "name": "PEQ Chain C",
            "default_code": "PEQ-DIRECT-C",
            "sale_ok": True,
        })
        cls.product_a.product_tmpl_id.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.link(cls.product_b.product_tmpl_id.id),
            ],
        })
        cls.product_b.product_tmpl_id.write({
            "direct_equivalent_product_tmpl_ids": [
                Command.link(cls.product_c.product_tmpl_id.id),
            ],
        })

    def _name_search(self, name, args=None, operator="ilike", limit=100):
        return self.env["product.product"]._name_search(
            name,
            args=args,
            operator=operator,
            limit=limit,
        )

    def test_search_expands_only_direct_neighbors(self):
        ids_from_a = self._name_search("PEQ-DIRECT-A", limit=False)
        ids_from_b = self._name_search("PEQ-DIRECT-B", limit=False)

        self.assertEqual(ids_from_a[0], self.product_a.id)
        self.assertIn(self.product_b.id, ids_from_a)
        self.assertNotIn(self.product_c.id, ids_from_a)
        self.assertEqual(ids_from_b[0], self.product_b.id)
        self.assertIn(self.product_a.id, ids_from_b)
        self.assertIn(self.product_c.id, ids_from_b)

    def test_native_first_limit_and_caller_domain_are_preserved(self):
        self.product_b.sale_ok = False
        args = [("sale_ok", "=", True)]

        limited_ids = self._name_search("PEQ-DIRECT-A", args=args, limit=1)
        expanded_ids = self._name_search("PEQ-DIRECT-A", args=args, limit=3)

        self.assertEqual(limited_ids, [self.product_a.id])
        self.assertEqual(expanded_ids, [self.product_a.id])
        self.assertEqual(args, [("sale_ok", "=", True)])

    def test_name_prefix_ranks_a_product_without_internal_reference_first(self):
        prefix_match = self.env["product.product"].create({
            "name": "WO120 WEGA",
            "sale_ok": True,
        })
        partial_code_match = self.env["product.product"].create({
            "name": "Filtro equivalente",
            "default_code": "X-WO120",
            "sale_ok": True,
        })

        ids = self._name_search("wo120", limit=8)

        self.assertEqual(ids[0], prefix_match.id)
        self.assertIn(partial_code_match.id, ids)

    def test_legacy_group_is_ignored_by_search(self):
        legacy_group = self.env["product.equivalent.group"].create({
            "name": "PEQ Legacy Search Group",
        })
        self.product_a.product_tmpl_id.equivalent_group_id = legacy_group
        self.product_c.product_tmpl_id.equivalent_group_id = legacy_group

        ids = self._name_search("PEQ-DIRECT-A", limit=False)

        self.assertIn(self.product_b.id, ids)
        self.assertNotIn(self.product_c.id, ids)

    def test_negative_and_empty_search_keep_native_behavior(self):
        negative_ids = self._name_search(
            "PEQ Chain A",
            args=[("id", "=", self.product_a.id)],
            operator="not ilike",
        )
        empty_ids = self._name_search(
            "",
            args=[("id", "in", [self.product_a.id, self.product_b.id])],
            limit=1,
        )

        self.assertEqual(negative_ids, [])
        self.assertEqual(len(empty_ids), 1)
        self.assertIn(empty_ids[0], [self.product_a.id, self.product_b.id])

    def test_direct_template_expands_all_target_variants(self):
        attribute = self.env["product.attribute"].create({
            "name": "PEQ Direct Size",
            "create_variant": "always",
        })
        value_one = self.env["product.attribute.value"].create({
            "name": "PEQ Direct One",
            "attribute_id": attribute.id,
        })
        value_two = self.env["product.attribute.value"].create({
            "name": "PEQ Direct Two",
            "attribute_id": attribute.id,
        })
        target_template = self.env["product.template"].create({
            "name": "PEQ Direct Variant Target",
            "attribute_line_ids": [Command.create({
                "attribute_id": attribute.id,
                "value_ids": [Command.set([value_one.id, value_two.id])],
            })],
        })
        self.product_a.product_tmpl_id.write({
            "direct_equivalent_product_tmpl_ids": [Command.link(target_template.id)],
        })

        ids = self._name_search("PEQ-DIRECT-A", limit=False)

        self.assertTrue(set(target_template.product_variant_ids.ids) <= set(ids))
