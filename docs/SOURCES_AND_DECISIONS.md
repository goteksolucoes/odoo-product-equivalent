# Sources and Architecture Decisions

## Upstream Odoo 16 references checked

- Odoo 16 ORM `name_search` documentation: relational autocomplete uses `name_search`; `product.product` provides a specialized `_name_search`.
- Odoo 16 `addons/product/models/product_product.py`: native `_name_search` prioritizes internal reference and barcode and then product name, with performance-conscious staged queries.
- Odoo 16 `addons/sale/views/sale_order_views.xml`: Sales Order `product_id` is `product.product`, uses sale/company domains and contextual values.
- Odoo 16 `addons/product/views/product_template_views.xml`: standard product template form XML ID and Sales page.
- Odoo 16 `addons/sale/views/sale_menus.xml`: standard Sales > Configuration > Products menu XML ID.
- Odoo 16 developer docs: manifests, XML/CSV data files, security ACLs, views and tests.

## OCA research

An OCA `odoo-pim` draft PR named `product_similarity` exists for 16.0, but its purpose is vector-based similarity/recommendation from characteristics. It is not the same deterministic commercial-equivalence requirement and is not used as a dependency or copied into this scaffold.

## Decision: extend, do not replace, native search

The addon calls `super()._name_search()` first and treats its results as anchors. This retains Odoo native matching behavior and reduces upgrade/performance risk. Equivalents are appended only after a native match is found.

## Decision: group-based equivalence

Each template belongs to zero or one equivalence group. This avoids maintaining bidirectional product-to-product links and provides a clean importable key for future implementations.

## Decision: template-level MVP

The initial module links templates rather than individual variants. Variant-level equivalence is deliberately deferred because silently mixing the two concepts creates incorrect substitutions for size/color/configuration variants.
