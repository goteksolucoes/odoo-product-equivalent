# Fluxo de busca de produtos — Odoo 16

Documento baseado na leitura do código local Odoo 16.0, build 20260717, revisão declarada `bb05e7d2a6276f158d14879fb8e8e9be33b2763d`. A instalação do addon foi informada pelo proprietário; este trace é estático e não equivale a um teste de autocomplete na interface.

Os caminhos de framework abaixo são relativos a `C:/Program Files/Odoo 16.0.20260717/server/odoo`. Os caminhos do addon são relativos à raiz deste repositório. Outros addons instalados podem acrescentar overrides ao fluxo; a cadeia completa de classes do registry não foi inspecionada neste documento.

## 1. Entrada na linha do pedido de venda

`addons/sale/models/sale_order_line.py:79` define `product_id` como Many2one para `product.product`. O domínio de venda exige `sale_ok=True` e produto compartilhado ou da empresa da linha.

`addons/sale/views/sale_order_views.xml:401` configura o campo na lista de linhas, com widget `sol_product_many2one` e contexto que inclui parceiro, quantidade, lista de preços, unidade de medida e empresa. O contexto não é um filtro por si só: ele fornece parâmetros aos métodos que o interpretam.

O widget é registrado em `addons/sale/static/src/js/sale_product_field.js:102`, com classe derivada de `Many2OneField` na linha 7. A seleção pode acionar o fluxo padrão de configuração de produtos; a busca de sugestões utiliza a infraestrutura relacional do web client.

## 2. Requisição do autocomplete

`addons/web/static/src/views/fields/relational_utils.js:233`, método `loadOptionsSource`, chama via ORM/RPC:

```text
modelo: product.product
método: name_search
name: texto digitado
operator: ilike
args: domínio calculado pelo campo
context: contexto do campo
limit: searchLimit + 1
```

Os valores padrão desse componente são `searchLimit=7` e `searchMoreLimit=320` (`:371`). Assim, a consulta inicial normalmente solicita 8 registros; o excedente permite oferecer “Pesquisar mais”. Esses valores são defaults do componente, não limites universais de toda chamada ao ORM.

O retorno contém pares `(id, nome de exibição)`, convertidos em opções pelo cliente. “Pesquisar mais” possui fluxo próprio, incluindo nova busca e diálogo de seleção (`:336`); não deve ser tratado como simples repetição visual do dropdown.

## 3. Método público e representação dos resultados

`models.py:1606`, `name_search`, chama `self._name_search(...)` para obter IDs e retorna `self.browse(ids).sudo().name_get()`.

Esse `sudo()` pertence ao framework e ocorre na formação dos nomes dos IDs já encontrados. O addon não acrescenta elevação de acesso à expansão da busca. A seleção de IDs e a formação dos rótulos são etapas diferentes.

`addons/product/models/product_product.py:418`, `name_get`, monta a representação do produto, considerando referência interna, nome, variantes e contexto de fornecedor quando aplicável.

## 4. Prioridades da busca nativa de produtos

A implementação especializada está em `addons/product/models/product_product.py:498`:

1. Para operadores positivos suportados (`=`, `ilike`, `=ilike`, `like`, `=like`), procura correspondência exata de `default_code`.
2. Se não encontrar, procura correspondência exata de `barcode`.
3. Sem resultado exato e com operador não negativo, procura referência interna com o operador recebido; depois completa o saldo do limite com busca por nome, excluindo IDs já encontrados.
4. Para operadores negativos, usa domínio específico combinando referência e nome. Não é apenas a inversão da busca positiva.
5. Ainda sem resultados e com operador positivo, tenta extrair uma referência entre colchetes, como `[ABC-001] Nome`, e procura essa referência exata.
6. Ainda sem resultados e com `partner_id` no contexto, procura código/nome em `product.supplierinfo` do parceiro e usa as informações de fornecedor para localizar produtos.
7. Com texto vazio, executa `_search(args, ...)`, sem critérios textuais adicionais.

Um resultado exato por referência ou código de barras impede a passagem pelas buscas textuais posteriores. As etapas não são reunidas em um único grande domínio OR: o código nativo separa as consultas por desempenho.

### Particularidades verificadas nesta revisão do framework

- O ramo final de fornecedor não concatena `args` na consulta de produtos. Logo, a afirmação de que todos os caminhos nativos aplicam o domínio do chamador precisa dessa ressalva.
- A consulta textual por `default_code` não recebe explicitamente `access_rights_uid=name_get_uid`, enquanto outras consultas o recebem. O addon não modifica essa assimetria do core.
- Estas são observações do código local, não correções implementadas nem falhas reproduzidas em runtime. A cobertura de fornecedor/domínio e usuário alternativo permanece relevante para testes de regressão.

## 5. Ponto de extensão do Product Equivalents

`models/product_product.py:9` sobrescreve `_name_search` com a assinatura Odoo 16 e chama `super()` primeiro. A implementação nativa descrita acima produz as âncoras da equivalência.

```text
Digitação na linha de venda
  → autocomplete relacional
  → product.product.name_search
  → product_equivalent._name_search
      → super()._name_search: busca nativa
      → IDs nativos
      → templates das âncoras → grupos de equivalência
      → _search de equivalentes com domínio original e saldo do limite
      → IDs nativos + IDs equivalentes
  → name_get: rótulos dos resultados
  → opções no dropdown
  → vendedor escolhe um produto
```

O addon não expande texto vazio, operadores negativos, ausência de resultados nativos ou limite já preenchido. Sem grupos nas âncoras, retorna os IDs nativos.

Havendo espaço, combina `args` com grupo pertencente aos grupos encontrados e exclusão dos IDs nativos, usando `expression.AND`. Executa `_search` sem `sudo()`, com `access_rights_uid=name_get_uid`, e acrescenta os novos IDs depois dos nativos. O filtro textual original não é reaplicado aos equivalentes: é justamente isso que permite oferecer um substituto com outro nome ou referência.

A equivalência pertence a `product.template`: variantes dos templates do grupo podem aparecer, sujeitas ao domínio e às regras de acesso. A ordem dos equivalentes é a ordem padrão da busca ORM, sem ranking por estoque ou preço. Sem limite, preserva a semântica de busca sem limite do ORM.

## 6. Segurança, efeitos e limites do trace

- A busca executa consultas de leitura; `browse` forma recordsets e o acesso aos campos pode carregar dados por prefetch.
- ACLs, regras de registro e contexto de ativos atuam no ORM; o domínio comercial do chamador é reutilizado explicitamente na expansão.
- A leitura das âncoras e grupos também está sujeita a acesso. A ausência de vazamentos ou exceções deve ser verificada com usuários reais de teste.
- O addon não cria linhas de venda nem adiciona equivalentes automaticamente. A escolha e os onchanges/configuradores posteriores pertencem a outra etapa do fluxo nativo.
- Este trace não prova quantidade de queries, desempenho em grande catálogo, cadeia de herança completa, nem comportamento de todos os módulos adicionais instalados.

## 7. Roteiro de validação no ambiente local

- Pesquisar referência exata, código de barras e nome; conferir âncora nativa primeiro.
- Pesquisar referência entre colchetes e referência de fornecedor com parceiro no contexto.
- Comparar produto sem grupo e produto com grupo; validar substitutos de outro nome/referência.
- Repetir com `sale_ok=False`, arquivados, empresas distintas e usuário com acesso limitado.
- Conferir duplicidades, limite preenchido, múltiplos grupos e variantes.
- Validar dropdown e “Pesquisar mais” separadamente.
- Escolher um equivalente e confirmar somente uma linha/produto selecionado.

Resultados reais devem ser registrados no checklist; instalação bem-sucedida não substitui esses testes.
