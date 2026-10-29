# Product Equivalents — Odoo 16

Reusable Odoo 16 addon for **commercially equivalent/substitute products**.

## Português (Brasil) — Produtos equivalentes

O **Product Equivalents** é um módulo para **Odoo 16** que permite organizar produtos comercialmente equivalentes, similares ou substitutos em grupos. Foi pensado para reutilização por empresas de diferentes segmentos em todo o Brasil, sem regras específicas de uma marca, cliente ou operação fiscal.

### Como funciona na venda

Ao pesquisar um produto no campo de produto de uma linha do pedido de venda, o Odoo mantém sua busca padrão. Se um dos produtos encontrados pertencer a um grupo de equivalência, os demais produtos desse grupo também poderão aparecer como opções.

Por exemplo, um grupo `FILTRO-001` pode reunir três produtos de referências diferentes: `AAA-001`, `BBB-001` e `CCC-001`. Ao pesquisar `AAA-001`, o vendedor poderá encontrar o produto original e as alternativas cadastradas no mesmo grupo, escolhendo apenas um deles para a linha do pedido.

Nenhum produto equivalente é adicionado automaticamente ao pedido. O módulo oferece alternativas de substituição; a escolha continua com o vendedor.

### Organização dos grupos

- Os grupos são cadastrados manualmente e vinculados aos produtos pelo formulário de produto.
- Cada modelo de produto pode pertencer a nenhum ou a um único grupo de equivalência.
- A equivalência é definida no nível do modelo de produto (`product.template`); suas variantes são consideradas candidatas na busca.
- A empresa é responsável por validar quais produtos podem ser considerados substitutos para sua aplicação. O cadastro no grupo não certifica compatibilidade técnica.

### Comportamento e escopo da primeira versão

Os resultados da busca padrão aparecem primeiro. Os equivalentes são acrescentados quando há espaço no limite de resultados, respeitando os filtros recebidos pela busca, como produtos disponíveis para venda e restrições de empresa.

Esta versão contempla grupos de equivalência e sua integração com a busca de produtos. Recursos como comparação de preços e estoque, ordenação por disponibilidade, importação de referências cruzadas e sugestões por inteligência artificial não fazem parte do escopo inicial.

### Instalação e situação do projeto

O nome técnico do módulo é `product_equivalent`. Para instalá-lo, coloque a pasta do módulo em um diretório de addons do Odoo 16, atualize a lista de aplicativos e instale **Product Equivalents**. Os exemplos de comandos estão na seção **Installation**, abaixo.

O projeto está em desenvolvimento e auditoria técnica. A instalação e os testes em uma base Odoo 16 de homologação devem ser concluídos antes do uso em produção.

## Business objective

When a salesperson searches for Product A in a Sales Order, Odoo should continue to return the normal match and may also return other products assigned to the same equivalence group. This is not an upsell/cross-sell feature: the salesperson chooses one product according to brand, price, availability, or commercial criteria.

## Example

Group `FILTER-001`:
- `AAA-001` — Brand A
- `BBB-001` — Brand B
- `CCC-001` — Brand C

Typing `AAA-001` in the product field can return A, B and C, while the salesperson selects only one.

## Architecture

- `product.equivalent.group`: reusable equivalence group.
- `product.template.equivalent_group_id`: links a product template to one group.
- `product.product._name_search()`: preserves native Odoo search, then appends products from the matched product's equivalence group.
- No JavaScript is required for the MVP.
- Caller domains (`sale_ok`, company restrictions, etc.) are preserved when equivalents are appended.

## Why a group instead of direct product-to-product links?

A group avoids a combinatorial many-to-many relationship. With four equivalent products, each product only points to the group rather than maintaining A↔B, A↔C, B↔C, etc.

## Installation

Copy `product_equivalent` into an Odoo addons path, update Apps List, then install **Product Equivalents**.

CLI example:

```bash
./odoo-bin -d DATABASE -i product_equivalent --stop-after-init
```

For upgrades:

```bash
./odoo-bin -d DATABASE -u product_equivalent --stop-after-init
```

## Standard Odoo 16 integration points

The scaffold uses the standard Odoo 16 XML IDs `product.product_template_only_form_view` and `sale.prod_config_main`. They were checked against the upstream Odoo 16 source. If a vendor distribution replaces core views/menus, revalidate the inherited XML IDs rather than patching Odoo core.

## MVP acceptance criteria

1. Product A and Product B can be assigned to one equivalence group.
2. Searching A's internal reference in a Sales Order returns A and B.
3. Searching B's internal reference returns B and A.
4. Unrelated products are not returned through equivalence expansion.
5. `sale_ok=False` products are not introduced when the caller's domain excludes them.
6. Multi-company domains passed by Sales remain respected.
7. Existing Odoo native name/code/barcode search continues working.
8. No optional product is automatically added to the order.

## Known MVP choices

- Equivalence is defined at **product template** level. All variants of templates in a group are treated as equivalent candidates. If variant-level equivalence is needed, make that a separate feature/version.
- Native results appear first; equivalents are appended.
- If native results already consume the requested autocomplete `limit`, the MVP does not force equivalents into the list. This protects native behavior and performance. A ranking strategy can be added later.

## Suggested roadmap

### 16.0.1.1.0
- Dedicated aliases/cross-reference codes.
- Search aliases without abusing `default_code`.

### 16.0.1.2.0
- Display stock and price context in a dedicated "Equivalent Products" chooser/action.
- Configurable ordering (stock, sequence, brand, price).

### 16.0.2.0.0
- Optional variant-level equivalence.
- Import wizard/API for cross-reference tables.

## License

LGPL-3 in this scaffold. Review your distribution strategy before publishing or mixing code from external addons with different licenses.
