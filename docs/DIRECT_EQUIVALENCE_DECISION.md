# Decisão funcional — equivalência direta

Status: requisito confirmado pelo proprietário; desenho técnico e implementação pendentes.

## Regra confirmada

A interface deve apresentar somente a grade de produtos equivalentes no formulário do produto, sem exigir nome ou código para um grupo.

A equivalência passa a ser uma relação direta entre modelos de produto, simétrica e sem transitividade:

- A vinculado a B: A lista B e B lista A.
- B vinculado a C: B lista C e C lista B.
- A não lista C, a menos que esse vínculo seja cadastrado explicitamente.
- O próprio produto não deve constar como seu equivalente.

Esta decisão substitui a arquitetura de grupos descrita na especificação inicial. A equivalência permanece no nível de `product.template`.

## Busca esperada

A expansão deve usar somente os vizinhos diretos dos resultados nativos. Não expandir novamente os equivalentes acrescentados.

Exemplo com referências exatas e vínculos A–B e B–C:

| Busca | Resultado esperado com espaço no limite |
| --- | --- |
| A | A primeiro, depois B; C ausente |
| B | B primeiro, depois A e C |
| C | C primeiro, depois B; A ausente |

Se a própria busca nativa encontrar vários produtos, seus vínculos diretos podem ser considerados. Isso não representa expansão transitiva.

Manter domínio do chamador, ACLs, regras de registro, contexto de ativos, limites, ausência de duplicidades e semântica de `name_get_uid` do Odoo 16.

## Implementação e transição

Forja prepara desenho mínimo e testes; Prisma revisa simetria, segurança, empresas e atualização do addon instalado. A sincronização inversa não pode servir de bypass genérico de permissões.

Não converter grupos legados automaticamente em vínculos entre todos os membros sem definir e documentar a política. Preparar transição idempotente, com tratamento explícito dos dados existentes. Os produtos WO120 e FO410B são o cenário de homologação indicado pelo proprietário.

Nenhuma alteração em banco ou código funcional foi feita como parte deste registro.
