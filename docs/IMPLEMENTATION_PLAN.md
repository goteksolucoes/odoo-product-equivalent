# Implementation Plan

## Phase 0 — Validate target Odoo build
- Confirm Odoo 16 Community/Enterprise edition and exact source revision.
- Confirm `product.product_template_only_form_view` XML ID.
- Confirm `sale.prod_config_main` menu XML ID.
- Confirm target addons path and deployment/update command.

## Phase 1 — Installable MVP
- Install addon on a development database.
- Fix any XML ID differences found in Phase 0.
- Create one equivalence group with two saleable products.
- Validate product form UX.
- Validate Sales Order autocomplete in browser.

## Phase 2 — Automated hardening
- Run module tests.
- Add multi-company tests.
- Add test for search by name and barcode/native code behavior.
- Add test for result limit and duplicates.
- Add test for archived/non-sale products.

## Phase 3 — UX improvements
- Make group membership easier to manage from product form/group form.
- Decide whether equivalent candidates need a visual marker.
- Optional dedicated action/button to compare equivalents with stock/prices.

## Phase 4 — Cross-reference aliases
Create a normalized alias model instead of overloading `default_code`:
- alias/reference code;
- product/template;
- optional manufacturer/brand/source;
- normalized value for search/import.

Then allow an alias to anchor the same equivalence expansion.

## Phase 5 — Packaging for reuse
- Generic README.
- Changelog.
- Translation template (`i18n/*.pot`).
- CI/lint conventions if publishing.
- Semantic Odoo versioning: `16.0.x.y.z`.
- License review.
