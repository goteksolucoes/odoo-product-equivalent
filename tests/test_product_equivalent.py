from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, new_test_user


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

    def test_template_autocomplete_keeps_exact_code_ahead_of_equivalents(self):
        Template = self.env["product.template"]
        equivalents = Template.create([
            {"name": "PEQ Ranking " + code, "default_code": code, "sale_ok": True}
            for code in ["FO410B", "W610", "W610/3"]
        ])
        anchor = Template.create({
            "name": "PEQ Ranking WO120",
            "default_code": "WO120",
            "sale_ok": True,
            "direct_equivalent_product_tmpl_ids": [Command.set(equivalents.ids)],
        })
        args = [
            ("sale_ok", "=", True),
            "|", ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
            ("name", "ilike", "PEQ Ranking "),
        ]
        Search = Template.with_context(
            company_id=self.env.company.id,
            quantity=1,
            display_default_code=True,
        )

        # Test the public RPC seam: core product.template reorders the variant
        # results by priority/name before this addon's template override runs.
        pairs = Search.name_search("wo120", args=args, operator="ilike", limit=8)
        limited = Search.name_search("wo120", args=args, operator="ilike", limit=1)

        self.assertEqual(pairs[0][0], anchor.id)
        self.assertEqual(set(dict(pairs)), set((anchor | equivalents).ids))
        self.assertEqual([pair[0] for pair in limited], [anchor.id])
        self.assertEqual(len(pairs), len(dict(pairs)))

        equivalents[0].sale_ok = False
        equivalents[1].active = False
        filtered = Search.name_search("wo120", args=args, limit=8)
        self.assertEqual(filtered[0][0], anchor.id)
        self.assertNotIn(equivalents[0].id, dict(filtered))
        self.assertNotIn(equivalents[1].id, dict(filtered))
        archived = Search.with_context(active_test=False).name_search(
            "wo120", args=args, limit=8,
        )
        self.assertEqual(archived[0][0], anchor.id)
        self.assertIn(equivalents[1].id, dict(archived))

    def test_template_autocomplete_keeps_name_prefix_ahead_of_partial_code(self):
        Template = self.env["product.template"]
        prefix = Template.create({"name": "PEQ-RANK-WO120 WEGA"})
        partial = Template.create({
            "name": "PEQ Ranking Partial",
            "default_code": "X-PEQ-RANK-WO120",
        })

        pairs = Template.name_search("peq-rank-wo120", limit=8)

        self.assertEqual(pairs[0][0], prefix.id)
        self.assertIn(partial.id, dict(pairs))

    def _multi_variant_ranking_products(self):
        attribute = self.env["product.attribute"].create({
            "name": "PEQ Ranking Size",
            "create_variant": "always",
            "value_ids": [
                Command.create({"name": "PEQ Ranking Small"}),
                Command.create({"name": "PEQ Ranking Large"}),
            ],
        })
        anchor = self.env["product.template"].create({
            "name": "ZZ PEQ Multi Variant Native",
            "attribute_line_ids": [Command.create({
                "attribute_id": attribute.id,
                "value_ids": [Command.set(attribute.value_ids.ids)],
            })],
        })
        anchor.product_variant_ids[0].default_code = "PEQ-MULTI-EXACT"
        anchor.product_variant_ids[1].default_code = "PEQ-MULTI-OTHER"
        equivalent = self.env["product.template"].create({
            "name": "PEQ-MULTI-EXACT similar",
            "default_code": "PEQ-EQUIVALENT-OTHER",
        })
        anchor.direct_equivalent_product_tmpl_ids = [Command.link(equivalent.id)]
        return anchor, equivalent

    def test_template_autocomplete_ranks_exact_variant_code_before_equivalent(self):
        anchor, equivalent = self._multi_variant_ranking_products()
        self.assertFalse(anchor.default_code)
        Search = self.env["product.template"].with_context(
            company_id=self.env.company.id, quantity=1, display_default_code=True,
        )
        args = [
            ("sale_ok", "=", True),
            "|", ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ]

        # The configurator calls the public template RPC, not _name_search on
        # product.product. The template has no code; its matching variant does.
        for query in ("PEQ-MULTI-EXACT", "peq-multi-exact"):
            for limit in (8, 1):
                with self.subTest(query=query, limit=limit):
                    pairs = Search.name_search(query, args=args, limit=limit)
                    self.assertEqual(
                        [record_id for record_id, _ in pairs],
                        [anchor.id, equivalent.id][:limit],
                    )

        # Exact native variant code ties with the equivalent's exact name.
        # Core template ordering puts the equivalent first alphabetically.
        equivalent.name = "PEQ-MULTI-EXACT"
        for limit in (8, 1):
            pairs = Search.name_search("PEQ-MULTI-EXACT", args=args, limit=limit)
            self.assertEqual(
                [record_id for record_id, _ in pairs],
                [anchor.id, equivalent.id][:limit],
            )

        equivalent.sale_ok = False
        pairs = Search.name_search("PEQ-MULTI-EXACT", args=args, limit=8)
        self.assertEqual([record_id for record_id, _ in pairs], [anchor.id])

    def test_template_autocomplete_does_not_rank_by_a_hidden_variant_code(self):
        anchor, equivalent = self._multi_variant_ranking_products()
        matching_variant = anchor.product_variant_ids.filtered(
            lambda product: product.default_code == "PEQ-MULTI-EXACT"
        )
        group = self.env["res.groups"].create({"name": "PEQ Variant Ranking Rule"})
        user = new_test_user(
            self.env,
            login="peq_multi_variant_ranking",
            groups="base.group_user",
            company_id=self.env.company.id,
            company_ids=[Command.set([self.env.company.id])],
        )
        user.groups_id = [Command.link(group.id)]
        self.env["ir.rule"].create({
            "name": "PEQ Hide Matching Variant",
            "model_id": self.env["ir.model"]._get("product.product").id,
            "domain_force": repr([("id", "!=", matching_variant.id)]),
            "groups": [Command.link(group.id)],
        })
        Search = self.env["product.template"].with_user(user)
        args = [
            ("sale_ok", "=", True),
            "|", ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ]

        # The visible equivalent is now the native text match. The template's
        # other, visible variant can expand back, but its hidden code cannot
        # contribute to ranking or be read through an elevated environment.
        for limit in (8, 1):
            pairs = Search.name_search("PEQ-MULTI-EXACT", args=args, limit=limit)
            self.assertEqual(
                [record_id for record_id, _ in pairs],
                [equivalent.id, anchor.id][:limit],
            )

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
