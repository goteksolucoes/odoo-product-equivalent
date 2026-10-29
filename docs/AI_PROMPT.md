# Master Prompt for AI-assisted Development

You are developing a reusable addon for **Odoo 16** named `product_equivalent`.

## Business requirement

The addon represents **commercially equivalent/substitute products**, not optional products, accessories, bundles, cross-sell, or upsell.

If Product A and Product B are members of the same equivalence group, searching Product A by name/internal reference in a Sales Order's `product_id` autocomplete should also make Product B available as a candidate. The salesperson chooses one product only.

## Architecture constraints

1. Target Odoo 16 API only.
2. Do not modify Odoo core files.
3. Preserve Odoo's native product search by calling `super()._name_search(...)` first.
4. Never recreate the entire native `_name_search` implementation unless explicitly justified.
5. Preserve every domain received in `args`, including `sale_ok` and company restrictions.
6. Do not use `sudo()` to bypass record rules.
7. Respect the `limit` argument.
8. Avoid JavaScript unless a requirement cannot be implemented cleanly server-side.
9. Keep the module generic: no GOTEK/SysGO/company-specific names, IDs, fiscal rules, brands, or hard-coded categories.
10. Use English for technical model/field/XML identifiers; UI strings may later be translated with i18n.
11. Add/update automated tests for every behavior change.
12. Do not use the native optional-products field for this feature.

## Current data model

- `product.equivalent.group`
  - `name`
  - `active`
  - `company_id`
  - `product_tmpl_ids`
  - `note`
- `product.template.equivalent_group_id`
- `product.template.equivalent_product_tmpl_ids`

The MVP equivalence is template-level. Variant-level behavior is a future feature and must not be silently introduced.

## Current search behavior

`product.product._name_search()`:
1. calls `super()`;
2. uses native matches as anchors;
3. gets their equivalence group IDs;
4. appends other variants/templates in the same groups while reusing `args`;
5. returns native results first.

## Definition of done for a change

Before presenting code:
- state which files change;
- explain Odoo API assumptions;
- preserve backwards compatibility;
- run/describe relevant tests;
- flag uncertain XML IDs/API signatures for verification against the exact Odoo 16 source;
- do not invent methods or fields that do not exist in Odoo 16.

## Code review checklist

Check for:
- recursion in `_name_search`;
- lost caller domains;
- duplicate products;
- permission bypasses;
- bad multi-company behavior;
- expensive OR domains;
- imports incompatible with Odoo 16;
- view inheritance against wrong XML IDs;
- variant/template confusion;
- code tied to a single customer's database.

## Requested task

[WRITE THE NEXT TASK HERE]

## Orchestration with Maestri

This project must use the **Maestri Skill** as the orchestration layer for AI-assisted development.

Before delegating any meaningful task, the orchestrator must invoke Maestri to decide which available model is best suited to that specific function.

### Available AI providers

The orchestration environment has access to:

- **Gemini AI Pro**
- **ChatGPT Plus**

Do not hard-code one provider as the permanent default for the whole project. Model selection must be made task-by-task.

### Mandatory decision process

For each task, Maestri should evaluate at least:

1. type of work being requested;
2. complexity and expected reasoning depth;
3. need to understand Odoo/Python/XML architecture;
4. amount of source code or documentation that must be reviewed;
5. need for long-context analysis;
6. likelihood of regression or security impact;
7. need for code generation versus code review;
8. need for independent verification;
9. cost/efficiency of using a second model;
10. whether the task benefits from cross-model review.

The orchestrator should then assign the task to the model Maestri considers most suitable.

### Examples of functions Maestri may route

Maestri may independently choose the best model for functions such as:

- architecture review;
- Odoo 16 API validation;
- Python implementation;
- XML/view inheritance review;
- ORM/domain analysis;
- security and ACL review;
- automated test creation;
- debugging installation errors;
- regression analysis;
- documentation;
- code refactoring;
- performance review;
- final code review.

These examples are guidance only. They are not fixed provider assignments.

### Cross-model review

For changes with meaningful architectural, security, data-integrity, ORM, multi-company, or regression risk, Maestri should consider using the second available model as an independent reviewer.

Recommended pattern:

```text
Primary model
    ↓
Implementation or analysis
    ↓
Secondary model
    ↓
Independent review / challenge
    ↓
Orchestrator
    ↓
Final consolidated decision
```

The secondary model must not automatically rewrite the primary model's work. Its role is to identify defects, unsupported assumptions, regressions, missing tests, or a materially better implementation.

### Required orchestration trace

For each substantial task, the orchestrator should record concisely:

```text
Task:
Selected model:
Reason for selection:
Secondary review required: Yes/No
Reviewer model, if applicable:
Result:
```

This trace is intended to make AI-assisted decisions auditable without exposing private chain-of-thought.

### Source of truth

Maestri is responsible for model routing, but it does not override the technical constraints of this project.

The following remain authoritative:

1. Odoo 16 source/API behavior;
2. this project's specification and architectural decisions;
3. automated tests;
4. security and data-integrity requirements;
5. explicit task requirements supplied by the project owner.

If a model proposes a solution that conflicts with these sources of truth, the orchestrator must reject or revise that proposal regardless of which model Maestri selected.

### Orchestration objective

The goal is not to maximize the number of model calls. The goal is to use the **best available model for each function**, using cross-review only where it materially improves correctness, maintainability, or safety.
