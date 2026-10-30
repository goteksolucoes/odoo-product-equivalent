# Registro de execução

## Auditoria inicial

- Task: auditar o scaffold sem alterar arquivos.
- Selected model: Codex / Forja.
- Reason for selection: análise de Python, ORM e XML e preparação de correções pequenas.
- Secondary review required: Yes.
- Reviewer model: Gemini / Prisma, revisão em andamento.
- Result: auditoria inicial entregue pelo Forja; achados de ACL, widget e integridade multiempresa pendentes de consolidação com evidências locais.

## Correções e testes do núcleo

- Task: corrigir os achados confirmados e preparar testes Odoo 16.
- Selected model: Codex / Forja; sessão ajustada pelo proprietário após limite de capacidade do modelo anterior.
- Reason for selection: continuidade da auditoria e implementação localizada com testes ORM.
- Secondary review required: Yes.
- Reviewer model: Gemini / Prisma.
- Result: retomada solicitada; alterações ainda não aplicadas ao projeto na última verificação.

O Forja possui exclusividade de edição em `models/`, `views/`, `security/`, `tests/` e `__manifest__.py`. Caso seu sandbox bloqueie esses diretórios, entregará patch na própria raiz permitida para revisão e aplicação pelo coordenador.

## Revisão independente

- Task: validar APIs, XML IDs, permissões e integridade multiempresa contra o código Odoo 16 local.
- Selected model: Gemini / Prisma (terminal identifica Gemini 4 Argon).
- Reason for selection: revisão por segundo modelo de alterações com impacto em segurança e ORM.
- Secondary review required: Yes.
- Reviewer model: Codex coordenador, na consolidação dos resultados.
- Result: análise em andamento. Avaliar especialmente grupo gestor escolhido e validação reversa ao alterar empresa do grupo.

## Restrições e decisões pendentes

- Não usar SQL para a validação reversa sem necessidade demonstrada e revisão independente. A proposta inicial foi retirada pelo implementador.
- Eventual leitura elevada exclusivamente para integridade deve ser justificada e revisada separadamente. A busca de equivalentes permanece sem `sudo()`.
- Não modificar base, serviços ou configurações externas nesta etapa.
- Dados de acesso permanecem na nota do canvas; não copiar para o repositório.
- A configuração `addons_path` precisa ser revalidada antes da instalação do addon.

## Revalidação do ranking — 30/10/2026

- Task: investigar o relato de perda de ordenação na busca da cotação, com revisão do Prisma e implementação pelo Forja, conforme pedido do proprietário.
- Assigned role / selected model: Forja, executor ChatGPT no papel existente; Prisma, revisor independente Gemini no papel existente. Nenhum agente adicional foi criado.
- Reason for selection: a investigação envolve o encadeamento entre `product.product` e `product.template`, ranking, limite e segurança. A revisão cruzada é necessária.
- Coordination: conexão direta Forja ↔ Prisma criada; Forja mantém exclusividade de edição em `models/` e `tests/` durante esta investigação.
- Baseline: `main=f91c4af`, `16.0=e5dfbf7`, `17.0=5e1999b`, `18.0=1fb5b33`, `19.0=3d1ad80`. Os commits mais recentes modificam README e imagens. `models/` é idêntico entre `main` e `16.0`; há diferenças anteriores de testes e CI entre essas branches.
- Local evidence: `addons_path` aponta para o diretório pai deste checkout. O log registra início do processo Odoo 16 PID 6516 em `2026-10-30 11:48:32 UTC` e carregamento de módulos às `12:04:47 UTC`, posterior à modificação dos fontes do ranking em 29/10. Isso não confirma o código de outro deploy nem reproduz o relato.
- Reproduction: termo, ordem esperada/observada e ambiente atual solicitados ao proprietário. WO120/FO410B é apenas o cenário histórico registrado em `DIRECT_EQUIVALENCE_DECISION.md`.
- Validation boundary: nenhuma execução de testes em banco, alteração de dados, atualização de módulo, reinício de serviço ou mudança de configuração autorizada ou realizada nesta rodada. Preparar comando e base isolada concretos antes de solicitar essa autorização.
- Confirmed defect: no Odoo 16, o segundo ranking de `product.template` usa `default_code=False` em templates com múltiplas variantes e perde a correspondência exata encontrada na variante. O replay dos métodos reais extraídos por AST retornou `[equivalente, nativo]` antes e `[nativo, equivalente]` após o patch, inclusive com `limit=1`. O defeito está nos commits `13a6d8f` / `1bae28d`; ainda não foi comprovado que seja o mesmo caso observado no deploy do proprietário.
- Independent review: Prisma aprovou estaticamente o patch e a reprodução em memória. Forja liberou a exclusividade após seu sandbox impedir a gravação na raiz; Codex aplicou o patch exato, SHA256 `66B9CB153A6DFDA2D12782E2C9C1CEF67DFAD361BAFAB72609754BC96FD1AC29`.
- Changes: `models/product_template.py` reaproveita o ranking das variantes; `tests/test_product_equivalent.py` acrescenta dois testes ORM para a API pública do autocomplete, limites 8/1, maiúsculas/minúsculas, desempate nativo, `sale_ok` e variante oculta por regra de acesso.
- Checks run: reprodução em memória pelo Forja e revisão Prisma; verificação de aplicação do patch, sintaxe Python dos dois arquivos e `git diff --check` pelo Codex. Nenhuma suíte ORM foi executada; o replay não comprova ACLs reais, SQL, registry do servidor ou latência.
- Result: correção Odoo 16 aplicada no checkout e revisada; testes ORM e homologação pendentes. Branches 17.0/18.0/19.0 não alteradas nesta rodada. Proposta concreta de validação em `RANKING_VALIDATION.md`; nenhum commit, push ou reinício realizado nesta rodada.

### Teste visual autorizado pelo proprietário

- Portal Maestri `Odoo`, localhost:8069: seis buscas na cotação (`wo120`, `WO120`, `wo12`, `fo410b`, `w610`, `w610/3`) priorizaram o código/prefixo pesquisado e exibiram equivalentes. Selecionar WO120 como alternativa incluiu somente uma linha. Cotação descartada sem salvar; produtos e relações não modificados.
- Evidências e ordens completas em `RANKING_VALIDATION.md` e `docs/qa/2026-10-30-ranking/`.
- A correção multivariante ainda não está homologada no browser: o processo local foi iniciado antes da gravação do patch e não há cenário multivariante preparado no catálogo visível. Nenhum reinício, atualização de módulo ou teste ORM foi executado. A autorização recebida nesta etapa se restringe ao teste visual pelo browser.

### Validação após reinício e solicitação de publicação

- O proprietário reiniciou o serviço e autorizou continuar. O novo PID 28328 carregou os módulos às 14:50:33 UTC, após a gravação do patch.
- Cenário criado pelo browser: template multivariante 9 com referências `QA-EXATO-20261030` / `QA-OUTRO-20261030` e equivalente 10 com nome prefixado pelo código pesquisado. Autocomplete em maiúsculas/minúsculas priorizou o nativo. Leituras RPC pela sessão do browser retornaram `[9]` com limite 1 e `[9, 10]` com limite 8 para ambos os termos. Suíte TransactionCase não executada.
- O proprietário confirmou sua própria validação e solicitou commit/push e atualização da produção. Encerrada a rodada adicional de testes; cotação descartada, fixtures arquivadas e configuração temporária de variantes restaurada. Produtos originais preservados.
- Publicação solicitada em main/16.0. Acesso conectado e configuração disponíveis apontam apenas para localhost; workflow identificado é de testes, sem deploy. Destino/procedimento de produção solicitado ao proprietário; não declarar produção atualizada apenas pelo push.
