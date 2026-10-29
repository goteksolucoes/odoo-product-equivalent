# Agent Model Usage Policy

## Objetivo

Esta política define como o orquestrador deve selecionar modelos para agents e subagents durante o desenvolvimento do projeto.

O objetivo principal é **preservar o orçamento de tokens e a capacidade dos modelos mais poderosos**, utilizando modelos mais leves e econômicos sempre que a tarefa puder ser executada com segurança por eles.

## Regra principal

> **Sempre crie agents e subagents com modelos mais fracos/econômicos para tarefas de implementação, manutenção, leitura, documentação, testes simples e trabalho repetitivo.**

Os modelos mais poderosos devem ser tratados como recursos escassos e utilizados apenas quando houver ganho técnico real.

Não utilize um modelo de alta capacidade apenas por conveniência.

## Princípio de escalonamento

Toda tarefa deve começar no menor nível de capacidade razoavelmente suficiente.

```text
Modelo econômico
      ↓
Executa a tarefa
      ↓
Resultado satisfatório?
   ┌──┴──┐
  Sim   Não
   │      ↓
   │   Modelo intermediário
   │      ↓
   │   Ainda há risco/dúvida?
   │      ↓
   │   Modelo mais poderoso
   │
   └──→ Concluir
```

O escalonamento deve ser progressivo.

## Tarefas adequadas para modelos mais fracos

Utilize agents com modelos mais leves para:

- criação de arquivos simples;
- ajustes de sintaxe;
- pequenas implementações;
- CRUD convencional;
- models simples;
- views XML;
- menus;
- ACLs básicas;
- documentação e README;
- comentários;
- organização de arquivos;
- renomeação de variáveis;
- formatação e tradução;
- testes unitários simples;
- criação de dados de teste;
- identificação de erros óbvios;
- análise de logs simples;
- atualização de documentação;
- tarefas repetitivas;
- revisão de estilo;
- comparação de arquivos;
- busca por referências no repositório.

## Quando usar modelos mais poderosos

Reserve modelos fortes para:

### Arquitetura
- decisões estruturais;
- mudanças no modelo de dados;
- alterações que afetam vários módulos;
- decisões difíceis de compatibilidade.

### ORM e internals do Odoo
- `_name_search`;
- `search`;
- `create`;
- `write`;
- `unlink`;
- recordsets complexos;
- multiempresa;
- contexto e domínios complexos.

### Segurança
- ACLs complexas;
- record rules;
- permissões multiempresa;
- exposição de dados;
- análise de `sudo()`;
- riscos de privilege escalation.

### Bugs difíceis
- regressões sem causa clara;
- bugs entre vários módulos;
- comportamento inconsistente;
- problemas complexos de contexto.

### Performance
- N+1 queries;
- gargalos ORM;
- busca em grande volume;
- métodos muito chamados.

### Revisão crítica
- alterações que afetam produção;
- mudanças em comportamento central;
- revisão antes de release.

## Política específica do `product_equivalent`

Devem começar em modelos econômicos:

```text
Criar model
Criar view
Criar menu
Criar ACL
Atualizar README
Criar testes básicos
Adicionar traduções
```

Podem justificar modelo mais forte:

```text
Modificar product.product._name_search()
Analisar domain
Garantir limit
Analisar variantes
Analisar multiempresa
Revisar segurança
Investigar regressões
```

## Separação de papéis

```text
Orchestrator
│
├── Implementation Agent
│   └── modelo econômico
├── Test Agent
│   └── modelo econômico
├── Documentation Agent
│   └── modelo econômico
├── Research Agent
│   └── modelo econômico/intermediário
└── Reviewer / Architect
    └── modelo mais poderoso
```

## Revisão cruzada

Para mudanças de alto impacto:

```text
Implementation Agent
Modelo econômico
      ↓
Test Agent
Modelo econômico
      ↓
Reviewer
Modelo poderoso
```

O modelo poderoso deve revisar apenas os pontos críticos, sem repetir desnecessariamente todo o trabalho.

## Regra de contexto

Não envie automaticamente todo o histórico ou repositório para modelos poderosos.

Forneça somente o contexto necessário para a decisão ou revisão.

## Critério de escalonamento

Antes de usar um modelo mais poderoso, avalie:

1. O modelo atual não consegue resolver a tarefa com segurança?
2. Existe decisão arquitetural relevante?
3. Existe risco de perda ou exposição de dados?
4. Existe risco significativo de regressão?
5. O comportamento envolve internals complexos do Odoo?
6. Os testes falharam de forma não óbvia?
7. Existem múltiplas soluções com trade-offs importantes?

Se todas forem **não**, mantenha a tarefa no modelo mais econômico.

## Maestri

Quando a Skill Maestri estiver disponível, ela deve ser usada para ajudar na seleção do modelo.

A política padrão permanece:

> **Preferir o modelo menos poderoso capaz de executar a tarefa com qualidade e segurança.**

O Maestri deve considerar dificuldade, risco, custo de contexto, necessidade de raciocínio, necessidade de revisão, impacto arquitetural e criticidade.

## Registro de decisão

Para tarefas relevantes:

```text
Task:
Assigned role:
Selected model:
Model tier: Economic / Intermediate / Powerful
Reason:
Escalation required: Yes/No
Reviewer required: Yes/No
```

## Regra de fallback

Se um modelo leve:

- não concluir a tarefa;
- produzir implementação incorreta;
- falhar repetidamente nos testes;
- demonstrar dificuldade com o contexto;
- propor alterações perigosas;

o orquestrador deve escalonar:

```text
Economic
   ↓ falhou
Intermediate
   ↓ falhou ou risco elevado
Powerful
```

Não insistir indefinidamente no mesmo modelo apenas para economizar tokens.

## Regra final

> **Modelos leves constroem. Modelos fortes decidem e revisam.**

```text
Implementação → modelo econômico
Testes → modelo econômico
Documentação → modelo econômico
Pesquisa → modelo econômico/intermediário
Arquitetura → modelo poderoso
Bug complexo → modelo poderoso
Segurança → modelo poderoso
Revisão crítica → modelo poderoso
```

O objetivo não é apenas reduzir consumo, mas utilizar cada modelo onde ele gera maior valor.
