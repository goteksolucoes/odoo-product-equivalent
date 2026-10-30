import os

from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.modules.migration import load_script
from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, new_test_user


class TestDirectEquivalentMigration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        migration_path = os.path.join(
            get_module_path("product_equivalent"),
            "migrations",
            "16.0.2.0.0",
        )
        cls.post_migration = load_script(
            os.path.join(migration_path, "post-migration.py"),
            "product_equivalent_test_post_migration",
        )

    def _legacy_group(self, name, products, active=True):
        group = self.env["product.equivalent.group"].create({
            "name": name,
            "active": active,
        })
        members = self.env["product.template"]
        for values in products:
            members |= self.env["product.template"].create(dict(
                values,
                equivalent_group_id=group.id,
            ))
        return group, members

    def test_compatible_pair_migrates_once_and_rerun_is_idempotent(self):
        group, members = self._legacy_group(
            "PEQ WO120 FO410B",
            [
                {"name": "WO120", "company_id": self.env.company.id},
                {"name": "FO410B", "company_id": self.env.company.id},
            ],
        )
        first, second = members

        self.post_migration.migrate(self.env.cr, "16.0.1.0.0")
        self.post_migration.migrate(self.env.cr, "16.0.1.0.0")
        group.invalidate_recordset(["active"])
        members.invalidate_recordset(["direct_equivalent_product_tmpl_ids"])

        self.assertEqual(first.direct_equivalent_product_tmpl_ids, second)
        self.assertEqual(second.direct_equivalent_product_tmpl_ids, first)
        self.assertEqual(first.equivalent_group_id, group)
        self.assertEqual(second.equivalent_group_id, group)
        group.invalidate_recordset(["active"])
        self.assertFalse(group.active)

        first.write({"direct_equivalent_product_tmpl_ids": [Command.unlink(second.id)]})
        self.post_migration.migrate(self.env.cr, "16.0.1.0.0")
        members.invalidate_recordset(["direct_equivalent_product_tmpl_ids"])
        self.assertFalse(first.direct_equivalent_product_tmpl_ids)
        self.assertFalse(second.direct_equivalent_product_tmpl_ids)

    def test_inactive_group_is_preserved_without_direct_edges(self):
        group, members = self._legacy_group(
            "PEQ Inactive Legacy",
            [{"name": "PEQ Inactive A"}, {"name": "PEQ Inactive B"}],
            active=False,
        )

        self.post_migration.migrate(self.env.cr, "16.0.1.0.0")

        self.assertFalse(members.mapped("direct_equivalent_product_tmpl_ids"))
        self.assertEqual(members.mapped("equivalent_group_id"), group)

    def test_active_pair_with_archived_member_migrates_without_reactivation(self):
        group, members = self._legacy_group(
            "PEQ Active Group Archived Member",
            [{"name": "PEQ Live Member"}, {"name": "PEQ Archived Member"}],
        )
        live, archived = members
        archived.active = False

        self.post_migration.migrate(self.env.cr, "16.0.1.0.0")
        group.invalidate_recordset(["active"])
        members.invalidate_recordset(["direct_equivalent_product_tmpl_ids"])

        self.assertFalse(group.active)
        self.assertFalse(archived.active)
        self.assertIn(
            archived,
            live.with_context(active_test=False).direct_equivalent_product_tmpl_ids,
        )
        self.assertIn(
            live,
            archived.with_context(active_test=False).direct_equivalent_product_tmpl_ids,
        )

    def test_more_than_two_active_members_abort_post_migration(self):
        group, _members = self._legacy_group(
            "PEQ Ambiguous Three",
            [
                {"name": "PEQ Ambiguous A"},
                {"name": "PEQ Ambiguous B"},
                {"name": "PEQ Ambiguous C"},
            ],
        )

        with self.assertRaises(UserError) as caught:
            self.post_migration.migrate(self.env.cr, "16.0.1.0.0")

        self.assertIn(group.name, str(caught.exception))

    def test_incompatible_company_pair_aborts_post_migration(self):
        company_b = self.env["res.company"].create({"name": "PEQ Migration B"})
        group, _members = self._legacy_group(
            "PEQ Incompatible Pair",
            [
                {"name": "PEQ Company A", "company_id": self.env.company.id},
                {"name": "PEQ Company B", "company_id": company_b.id},
            ],
        )

        with self.assertRaises(UserError) as caught:
            self.post_migration.migrate(self.env.cr, "16.0.1.0.0")

        self.assertIn(group.name, str(caught.exception))


class TestLegacyGroupIsReadOnly(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_manager = new_test_user(
            cls.env,
            login="peq_legacy_read_only_manager",
            groups="sales_team.group_sale_manager",
            company_id=cls.env.company.id,
            company_ids=[Command.set([cls.env.company.id])],
        )

    def test_sale_manager_cannot_create_or_modify_legacy_group(self):
        group = self.env["product.equivalent.group"].create({
            "name": "PEQ Legacy Read Only",
        })
        Group = self.env["product.equivalent.group"].with_user(self.sale_manager)

        self.assertEqual(Group.browse(group.id).name, group.name)
        with self.assertRaises(AccessError):
            Group.create({"name": "PEQ Forbidden Legacy Group"})
        with self.assertRaises(AccessError):
            Group.browse(group.id).write({"note": "Forbidden"})

    def test_legacy_menu_is_inactive_and_product_form_shows_only_direct_grid(self):
        menu = self.env.ref("product_equivalent.product_equivalent_group_menu")
        view = self.env.ref("product_equivalent.product_template_form_view_equivalent")

        self.assertFalse(menu.active)
        self.assertIn("direct_equivalent_product_tmpl_ids", view.arch_db)
        self.assertNotIn("equivalent_group_id", view.arch_db)
