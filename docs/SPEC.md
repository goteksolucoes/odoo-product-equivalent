# Functional and Technical Specification

## 1. Problem

Odoo's optional products are cross-selling/upselling. The required behavior is substitution: several SKUs can satisfy the same commercial need, and the salesperson must choose one.

## 2. Scope — MVP

### In scope
- Manual equivalence groups.
- Assignment from product template.
- Automatic expansion in `product.product` name search.
- Sales Order compatibility.
- Access rights and basic multi-company support.
- Automated Python tests.

### Out of scope
- Automatic similarity scoring/ML/vector search.
- Automatic replacement of order lines.
- Adding multiple equivalent products to an order.
- Stock reservation logic.
- Purchase/manufacturing substitution.
- Price comparison popup.
- Alias tables (planned extension).

## 3. Data model

### `product.equivalent.group`
- `name`: required Char, indexed.
- `active`: Boolean.
- `company_id`: optional Many2one to `res.company`; empty means shared/global.
- `product_tmpl_ids`: One2many to `product.template`.
- `note`: Text.

### `product.template`
- `equivalent_group_id`: Many2one to group, indexed, `check_company=True`.
- `equivalent_product_tmpl_ids`: related/read-only One2many for UX.

## 4. Search algorithm

Pseudo-code:

```text
native_ids = super()._name_search(...)

if no query OR negative operator OR no native match:
    return native_ids

find equivalence groups from native matched products

if no group:
    return native_ids

search product.product where:
    original caller domain still applies
    AND product template belongs to matched groups
    AND id is not already in native_ids

return native_ids + equivalent_ids, respecting limit
```

### Rationale
Do not reimplement Odoo's native code/name/barcode/supplier search. The addon extends results after core logic has resolved the initial products.

## 5. Security

- Internal users: read group definitions.
- Product managers: CRUD group definitions.
- Product/product template ACLs remain governed by Odoo core.
- Never use `sudo()` in search expansion.

## 6. Multi-company

The equivalent search reuses `args` provided by the calling field. Sales Order already provides a company-aware domain. The group itself can be global (`company_id=False`) or company-specific.

Tests should be expanded for multi-company before production rollout in a multi-company database.

## 7. Performance principles

- Index group link (`equivalent_group_id`).
- Do not add unbounded OR conditions to Odoo's native product query.
- Do not replace `_name_search` internals; call `super()` first.
- Respect autocomplete `limit`.
- Avoid `sudo()`.
- Benchmark on realistic product counts (10k, 50k, 100k SKUs if relevant).

## 8. Upgrade compatibility

This addon uses ORM inheritance and view inheritance only. It must not edit Odoo core files. Before migrating major Odoo versions, review:
- `_name_search` signature/behavior;
- Sale Order product field/widget;
- inherited product form XML IDs;
- product/company domain changes.

## 9. Acceptance tests

- Search by exact internal reference.
- Search by product name.
- Search product without group.
- Exclude non-sale product using caller domain.
- No duplicate IDs.
- Result limit respected.
- Access rules respected.
- Company domain respected.
- Product with variants (document expected behavior).
