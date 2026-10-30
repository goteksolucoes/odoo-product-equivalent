# Plano de trabalho — Product Equivalent

Atualizado em 29/10/2026. Este checklist registra a implementação de equivalência direta, simétrica e não transitiva, e separa validação automatizada de homologação no Odoo local.

## Estado atual

- Checkout principal `main` permanece no baseline Odoo 16 (`cf44ed1`); os ports foram trabalhados e publicados isoladamente nas branches de versão.
- Addon Odoo 16: versão `16.0.2.0.0`, instalado no ambiente local.
- Equivalência: relação direta entre templates, simétrica e não transitiva; a ficha do produto usa uma grade de seleção.
- Manifesto: autor, site, ícone e categoria ajustados; o usuário confirmou que os metadados aparecem no Odoo.
- Branch `16.0` mantém a base compatível e agora tem workflow OCA; `17.0`, `18.0` e `19.0` foram portadas. Odoo e OCB passaram com 32/32 testes em cada branch.

| Branch | Commit | CI Odoo | CI OCB |
|---|---|---|---|
| `19.0` | `a1ea3ae` | 32/32 | 32/32 |
| `18.0` | `5682c74` | 32/32 | 32/32 |
| `17.0` | `bc0edef` | 32/32 | 32/32 |
| `16.0` | `8ba6411` | 32/32 | 32/32 |

Execuções: [CI 19.0](https://github.com/goteksolucoes/odoo-product-equivalent/actions/runs/40971959147), [CI 18.0](https://github.com/goteksolucoes/odoo-product-equivalent/actions/runs/40974776903), [CI 17.0](https://github.com/goteksolucoes/odoo-product-equivalent/actions/runs/40976387989), [CI 16.0](https://github.com/goteksolucoes/odoo-product-equivalent/actions/runs/40977877659).

## Prioridade 0 — homologar a experiência no Odoo 16 local

- [ ] Executar a suíte ORM completa em banco descartável isolado no Odoo 16 e registrar comando, versão e resultado.
- [ ] Verificar a tradução PT-BR na ficha do produto e na tela de aplicativos após atualizar o módulo e o idioma.
- [ ] Validar no formulário de venda o ranking por similaridade e confirmar que os produtos equivalentes diretos continuam aparecendo sem alterar domínio ou limite.
- [ ] Registrar evidência visual da tradução, da grade e do autocomplete.

**Critério de saída:** suíte Odoo 16 sem falhas conhecidas, rótulos PT-BR visíveis e autocomplete homologado na interface.

## Prioridade 1 — fechar governança das branches

- [x] Criar workflows de testes OCA para `16.0`, `17.0`, `18.0` e `19.0`.
- [x] Portar o código e os testes para Odoo `17.0`, `18.0` e `19.0` em commits separados.
- [x] Passar os testes de instalação e do addon em Odoo e OCB nas quatro branches.
- [ ] Confirmar a branch padrão configurada no GitHub e decidir se `19.0` deve ser a padrão do repositório.
- [ ] Adicionar os arquivos de cada versão às convenções OCA de pre-commit, metadados e documentação, se aplicável.

## Prioridade 2 — documentação e releases

- [ ] Atualizar `README.md`, `SPEC.md`, `AI_PROMPT.md`, `SOURCES_AND_DECISIONS.md` e `PRODUCT_SEARCH_FLOW.md` para refletir a grade direta, simetria, não transitividade e ranking.
- [ ] Documentar requisitos e comandos de desenvolvimento por versão Odoo.
- [ ] Publicar matriz de versões suportadas e changelog após a homologação local do Odoo 16.
- [ ] Revisar diffs, traduções e arquivos incluídos antes de cada release; não incluir credenciais.

## Critério de suporte

Uma versão só é considerada validada quando a CI OCA conclui com sucesso nos jobs Odoo e OCB. A homologação da interface e a tradução PT-BR do ambiente local continuam sendo verificações separadas.
