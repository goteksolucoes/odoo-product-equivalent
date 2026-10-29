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
