from odoo.tests.common import SavepointCase


class TestProductEquivalent(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env["product.equivalent.group"].create({"name": "FILTER-001"})
        cls.product_a = cls.env["product.product"].create({
            "name": "Filter Brand A",
            "default_code": "AAA-001",
            "sale_ok": True,
            "equivalent_group_id": cls.group.id,
        })
        cls.product_b = cls.env["product.product"].create({
            "name": "Filter Brand B",
            "default_code": "BBB-001",
            "sale_ok": True,
            "equivalent_group_id": cls.group.id,
        })
        cls.unrelated = cls.env["product.product"].create({
            "name": "Unrelated Product",
            "default_code": "CCC-001",
            "sale_ok": True,
        })

    def test_search_by_internal_reference_returns_equivalent(self):
        ids = self.env["product.product"]._name_search(
            "AAA-001", args=[("sale_ok", "=", True)], operator="ilike", limit=100
        )
        self.assertIn(self.product_a.id, ids)
        self.assertIn(self.product_b.id, ids)
        self.assertNotIn(self.unrelated.id, ids)

    def test_native_search_without_group_is_unchanged(self):
        ids = self.env["product.product"]._name_search(
            "CCC-001", args=[("sale_ok", "=", True)], operator="ilike", limit=100
        )
        self.assertIn(self.unrelated.id, ids)
        self.assertNotIn(self.product_a.id, ids)
        self.assertNotIn(self.product_b.id, ids)

    def test_sale_domain_is_respected(self):
        self.product_b.sale_ok = False
        ids = self.env["product.product"]._name_search(
            "AAA-001", args=[("sale_ok", "=", True)], operator="ilike", limit=100
        )
        self.assertIn(self.product_a.id, ids)
        self.assertNotIn(self.product_b.id, ids)
