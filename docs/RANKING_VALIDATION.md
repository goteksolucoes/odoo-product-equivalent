# Validação da correção de ranking — Odoo 16

**Situação final:** revisão estática aprovada pelo Prisma, reprodução sem banco
aprovada e validação pelo navegador concluída após reinício feito pelo
proprietário. O proprietário também informou ter validado o comportamento e
solicitou commit/push. A suíte automatizada `TransactionCase` local não foi
executada; ela permanece como cobertura de regressão preparada para a CI.

O patch revisado pelo Prisma e preparado pelo Forja está aplicado no checkout.
Quando um template tem múltiplas variantes, sua referência interna pode ser vazia.
O segundo ranking agora considera a referência encontrada na variante, para que
um equivalente por prefixo não ultrapasse o código exato pesquisado.

A reprodução em memória executou métodos reais do core e do addon extraídos por
AST. Antes: `[equivalente, nativo]`; após: `[nativo, equivalente]`. Com limite 1,
o código exato permanece como único resultado. Esse ensaio não substitui testes
ORM nem demonstra que o defeito reproduzido corresponde ao relato do deploy.

## Proposta de teste isolado — ainda não executada

Mediante autorização, confirmar que `peq_ranking_regression_20261030` não existe
e criar/inicializar exclusivamente essa base descartável no PostgreSQL local.
O teste lê a configuração existente; usa diretório de dados e log separados,
sem HTTP ou cron. A base de uso normal e o serviço Odoo não são atualizados.
Não é um servidor PostgreSQL separado.

```powershell
& 'C:/Program Files/Odoo 16.0.20260717/python/python.exe' `
  'C:/Program Files/Odoo 16.0.20260717/server/odoo-bin' `
  -c 'C:/Program Files/Odoo 16.0.20260717/server/odoo.conf' `
  --addons-path 'C:/Program Files/Odoo 16.0.20260717/server/odoo/addons,C:/Users/CAMPEAO LUB/Documents/odoo' `
  -d peq_ranking_regression_20261030 `
  --db-filter '^peq_ranking_regression_20261030$' `
  -i product_equivalent --without-demo=all --test-enable `
  --test-tags '/product_equivalent:TestDirectEquivalentSearch.test_template_autocomplete_ranks_exact_variant_code_before_equivalent,/product_equivalent:TestDirectEquivalentSearch.test_template_autocomplete_does_not_rank_by_a_hidden_variant_code' `
  --no-http --max-cron-threads=0 --stop-after-init `
  --data-dir 'C:/Users/CAMPEAO LUB/Documents/odoo/product_equivalent/.maestri/roles/a6f5ca5e-a7f0-4753-bdce-81b757545e27/odoo-test-data' `
  --logfile 'C:/Users/CAMPEAO LUB/Documents/odoo/product_equivalent/.maestri/roles/a6f5ca5e-a7f0-4753-bdce-81b757545e27/odoo-ranking-test.log'
```

Os dois testes preparados cobrem a API `product.template.name_search` usada pelo
autocomplete, limites 8 e 1, maiúsculas/minúsculas, desempate nativo, filtro de
venda e variante oculta por regra de acesso. A aprovação final depende de sua
execução e da homologação do caso concreto no ambiente afetado.

## Teste visual autorizado — 30/10/2026

Executado pelo portal Maestri `Odoo`, em `http://localhost:8069`, sessão
Administrator, formulário de cotação nova sem cliente e sem salvar.

| Busca | Ordem observada no autocomplete | Resultado |
|---|---|---|
| `wo120` | WO120, W610, FO410B, W610/3 | Código pesquisado primeiro |
| `WO120` | WO120, W610, FO410B, W610/3 | Mesma ordem com maiúsculas |
| `wo12` | WO120, W610, FO410B, W610/3 | Prefixo pesquisado primeiro |
| `fo410b` | FO410B, WO120, 0986B00015 | Código pesquisado primeiro |
| `w610` | W610, W610/3, WO120, 0986B00015 | Código exato antes do prefixo |
| `w610/3` | W610/3, WO120, 0986B00015 | Código com barra primeiro |

Ao pesquisar `w610/3` e selecionar o equivalente WO120, a tela apresentou uma
única linha com WO120. Nenhum equivalente adicional foi incluído automaticamente.
A cotação foi descartada pelo botão próprio, retornando à lista sem salvar.
Na ficha WO120, a grade de relações diretas exibia FO410B, W610 e W610/3,
coerentes com o autocomplete dessa busca.

Evidências visuais:

- [Busca WO120](qa/2026-10-30-ranking/quotation-wo120.png).
- [Busca FO410B](qa/2026-10-30-ranking/quotation-fo410b.png).
- [Seleção de somente um equivalente](qa/2026-10-30-ranking/quotation-single-selection.png).

Limites desta rodada: o catálogo visível continha sete produtos com referência
no template; não havia cenário multivariante preparado para o defeito específico.
Os seis casos acima validam o comportamento do servidor em execução e não
homologam o novo patch multivariante. O log registra início do PID 6516 às
11:48:32 UTC e carregamento de módulos às 12:04:47 UTC; o arquivo corrigido
`models/product_template.py` foi gravado às 14:38:28 UTC. Não houve reinício,
atualização de módulo, criação de produtos/atributos ou execução da suíte ORM.
É necessário carregar a correção no servidor e preparar um cenário apropriado
antes de declarar a regressão multivariante homologada visualmente.

## Validação após reinício — 30/10/2026

O proprietário reiniciou o serviço e autorizou seguir com o cenário de teste.
O log confirmou novo PID 28328, iniciado às 14:50:22 UTC, e módulos carregados
às 14:50:33 UTC, após a gravação do patch às 14:38:28 UTC.

Pelo navegador, foram criados exclusivamente estes registros identificados
como teste:

- Template 9: `ZZ QA Ranking 20261030 - Nativo multivariante`, sem referência
  interna própria, com duas variantes: `QA-EXATO-20261030` (ID 9, QA Pequeno)
  e `QA-OUTRO-20261030` (ID 10, QA Grande).
- Template 10: `QA-EXATO-20261030 similar TESTE`, referência
  `QA-EQUIV-20261030`, vinculado diretamente ao template 9.
- Atributo 1: `QA Ranking 20261030 - Tamanho`, valores QA Pequeno/QA Grande.

Na cotação sem salvar, a busca `QA-EXATO-20261030` e sua versão em minúsculas
apresentaram primeiro o template multivariante e depois o equivalente por
prefixo. O [snapshot do autocomplete](qa/2026-10-30-ranking/multivariant-lowercase-snapshot.txt)
registra a ordem real da interface. A captura PNG desse novo cenário não ficou
disponível: o portal informou timeout de renderização da janela; as leituras de
interface e as interações continuaram funcionando.

Como complemento ao teste visual, a mesma sessão do browser chamou o método
de leitura `product.template.name_search`, com domínio de venda/empresa e
limites 1 e 8. Resultados reais do servidor:

| Termo | Limite | IDs retornados |
|---|---|---|
| `QA-EXATO-20261030` | 1 | `[9]` |
| `QA-EXATO-20261030` | 8 | `[9, 10]` |
| `qa-exato-20261030` | 1 | `[9]` |
| `qa-exato-20261030` | 8 | `[9, 10]` |

Essas chamadas de leitura pelo browser não são a execução da suíte ORM
isolada proposta acima. O desempate nativo e a regra de acesso continuam
cobertos pelos testes preparados e pelo replay/revisão nos limites descritos.
O teste adicional de empate de nome na interface foi interrompido quando o
proprietário informou sua própria validação e solicitou publicar a correção.

Ao encerrar, a cotação foi descartada sem salvar e os dois templates de teste
foram arquivados. Os sete produtos preexistentes não foram alterados. A opção
de variantes, ativada para preparar o cenário, foi restaurada ao estado anterior.

## Publicação e produção

A correção é específica das APIs do Odoo 16 e deve ser publicada em `main` e
`16.0`. As branches 17.0/18.0/19.0 precisam de adaptação e revisão específicas;
não devem receber o arquivo Odoo 16 integralmente.

O repositório contém workflow de testes na branch 16.0, sem workflow de deploy
identificado. O único ambiente nos acessos conectados é localhost:8069. O push
por si só não comprova atualização de produção. Para aplicar no servidor, é
necessário identificar o checkout/deploy correto, atualizar o código Odoo 16 e
reiniciar seus processos para carregar o Python. Esta correção não acrescenta
campos, tabelas ou arquivos de dados ao addon.
