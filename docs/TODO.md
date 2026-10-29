# Plano de execução — Product Equivalents / Odoo 16

Checklist operacional da primeira versão. A especificação permanece em `SPEC.md` e as decisões em `SOURCES_AND_DECISIONS.md`. Atualizar os itens com evidências conforme o trabalho avançar; código escrito não significa comportamento validado.

## 1. Consolidar a auditoria do scaffold

- [x] Ler a nota `first-prompt` e a documentação e código existentes.
- [x] Criar o time: Codex coordenador, Forja para implementação e Prisma para revisão independente.
- [x] Disponibilizar as skills Odoo, revisão, rastreamento, testes e arquitetura.
- [ ] Consolidar os relatórios dos agentes em um diagnóstico único, com arquivos, linhas e fontes.
- [ ] Confirmar no código Odoo 16 os grupos de segurança, XML IDs, assinatura de `_name_search` e comportamento de `name_get_uid`.
- [ ] Rastrear o fluxo da seleção em vendas até a busca nativa e a expansão de equivalentes.
- [ ] Registrar por tarefa modelo executor, motivo, revisor e resultado, conforme `first-prompt`.

**Critério de avanço:** problemas confirmados separados de hipóteses, com plano mínimo de correção. Não acrescentar funcionalidades nesta etapa.

## 2. Preparar o ambiente local (em paralelo com a auditoria)

- [x] Concluir a instalação local do Odoo **16** e PostgreSQL (serviços em execução; versão confirmada no código local).
- [ ] Registrar edição, revisão do código, executável Python, configuração, porta e comando de inicialização em `docs/LOCAL_DEVELOPMENT.md`, sem senhas.
- [ ] Definir uma base exclusiva de desenvolvimento/testes.
- [ ] Configurar o diretório pai de `product_equivalent` no `addons_path` e confirmar que o nome técnico da pasta permanece `product_equivalent`.
- [ ] Confirmar que Vendas e as dependências do manifesto estão disponíveis.
- [ ] Registrar comandos reproduzíveis de instalação, atualização e execução de testes.
- [ ] Validar acesso do agente ao ambiente local e ao navegador para acompanhamento em tempo real.

**Critério de avanço:** Odoo 16 inicia e a base de desenvolvimento pode ser acessada. A ausência do runtime não impede auditoria, correções estáticas ou preparação dos testes.

## 3. Corrigir o núcleo com alterações pequenas

- [ ] Corrigir referências de grupos de segurança e menus, se confirmadas inválidas.
- [ ] Revisar ACLs, regras de registro e consistência de empresa entre grupos e produtos.
- [ ] Corrigir widgets e heranças XML incompatíveis com Odoo 16.
- [ ] Corrigir problemas confirmados da busca preservando `super()`, domínio original, regras de acesso, contexto, ordem nativa, ausência de duplicidade e limite.
- [ ] Preservar a equivalência no nível de `product.template` e documentar o comportamento das variantes.
- [ ] Conferir manifesto, imports e ordem de carregamento dos arquivos.

**Critério de avanço:** cada alteração resolve um achado identificado, sem `sudo()` na busca, JavaScript, novas dependências obrigatórias ou mudança da arquitetura de grupos.

## 4. Preparar e executar testes automatizados

- [ ] Produto sem grupo mantém o comportamento nativo.
- [ ] Busca por referência, nome e código de barras preserva os resultados nativos e expande os equivalentes aplicáveis.
- [ ] Produtos de outro grupo não entram na expansão.
- [ ] Domínio `sale_ok` e demais filtros do chamador são respeitados.
- [ ] Resultados não têm duplicidades e os nativos aparecem primeiro.
- [ ] Limites pequenos, limite já preenchido e busca sem limite seguem a semântica nativa.
- [ ] Produtos arquivados respeitam domínio e contexto.
- [ ] Múltiplos grupos nos resultados nativos são tratados corretamente.
- [ ] Busca vazia e operadores negativos preservam o comportamento esperado.
- [ ] Variantes respeitam a equivalência por template.
- [ ] Usuários reais de teste respeitam ACLs e regras de registro.
- [ ] Grupos compartilhados e específicos de empresa respeitam acesso e integridade em criação e alteração de vínculos.
- [ ] Instalar em base limpa e executar a suíte Odoo; registrar comando, revisão e resultado real.
- [ ] Atualizar o addon já instalado e verificar erros de carregamento ou regressões.

**Critério de avanço:** suíte passa no Odoo 16 local; qualquer teste não executado permanece explicitamente pendente.

## 5. Validar o fluxo real na interface

- [ ] Criar um grupo com produtos A e B e um produto C fora dele.
- [ ] Conferir cadastro do grupo, vínculo no formulário do produto e visualização dos membros.
- [ ] Em pedido de venda, pesquisar A e escolher B como alternativa.
- [ ] Confirmar que somente o produto escolhido é adicionado à linha.
- [ ] Repetir com produto não vendável, arquivado, limite de resultados e restrição de empresa.
- [ ] Registrar resultados e problemas reproduzíveis; corrigir e repetir apenas os cenários afetados.

**Critério de avanço:** fluxo comercial funciona na interface e corresponde aos testes automatizados.

## 6. Revisar e preparar a entrega

- [ ] Submeter mudanças de busca, ACLs e multiempresa à revisão independente do segundo modelo.
- [ ] Resolver os achados e repetir os testes afetados.
- [ ] Alinhar README em inglês e PT-BR, especificação e decisões com o comportamento final.
- [ ] Preparar tradução PT-BR da interface para distribuição nacional e validar os termos no Odoo.
- [ ] Registrar versão, changelog, instruções de instalação e limitações conhecidas.
- [ ] Verificar diff, arquivos indevidos e ausência de credenciais.
- [ ] Fazer commits por mudança coerente e enviar ao GitHub quando as permissões permitirem.
- [ ] Entregar relatório com alterações, revisões, testes executados e riscos remanescentes.

**Conclusão do MVP:** instalação e atualização válidas, busca nativa preservada, equivalentes corretos, segurança revisada, testes e fluxo real aprovados e documentação alinhada.

## Regras de execução

1. Coordenador consolida prioridades; Forja implementa; Prisma revisa de forma independente. Não editar o mesmo arquivo simultaneamente.
2. Trabalhar em ciclos curtos: achado → correção mínima → teste → revisão → registro.
3. Usar o código real do Odoo 16 como referência; não aplicar exemplos de versões posteriores sem validação.
4. A instalação local pode avançar em paralelo com as etapas que não dependem dela.
5. Manter aliases, IA, ranking por estoque/preço, wizard, OWL e eCommerce fora desta rodada.

**Próxima ação:** consolidar os achados da auditoria e confirmar as referências no Odoo 16; em paralelo, concluir e documentar o ambiente local.
