# Ambiente local de desenvolvimento

Verificado em 29/10/2026, sem alterações na base ou nos serviços.

- Instalação: `C:\Program Files\Odoo 16.0.20260717`.
- Versão confirmada em `server/odoo/release.py`: Odoo 16.0, build 20260717.
- Revisão Odoo declarada: `bb05e7d2a6276f158d14879fb8e8e9be33b2763d`.
- Serviço Odoo: `odoo-server-16.0`, em execução na verificação.
- Serviço PostgreSQL: `PostgreSQL_For_Odoo`, em execução na verificação.
- Configuração: `C:\Program Files\Odoo 16.0.20260717\server\odoo.conf`.
- Porta HTTP configurada: `8069`; endereço esperado: `http://localhost:8069`.
- PostgreSQL configurado em `localhost:5432`.

## Ajuste necessário

O `addons_path` inclui a pasta do próprio addon. O Odoo precisa do diretório pai para descobrir `product_equivalent`.

Preservar os demais diretórios configurados e substituir a entrada deste projeto por:

```ini
C:\Users\CAMPEAO LUB\Documents\odoo
```

Após salvar, reiniciar o serviço Odoo para aplicar a configuração.

## Pendências

- Confirmar acesso à interface e definir base exclusiva de desenvolvimento.
- Aplicar o ajuste do `addons_path` e confirmar descoberta do addon.
- Validar Python embarcado, dependências e comando de testes.
- Registrar comandos de instalação/atualização/testes após definir a base.

Não registrar senhas ou chaves neste documento.

## Validação de acesso

- Login web validado pelo portal `Odoo Local`, em `http://localhost:8069/web`: sessão autenticada e tela de Mensagens carregada.
- Conexão PostgreSQL validada em `localhost:5432`, na base `odoo`.
- Servidor retornou PostgreSQL 12.4.
- Consultas realizadas com `default_transaction_read_only=on`, confirmado por `transaction_read_only`.
- `base` e `sale_management` constam como instalados; `product_equivalent` ainda não consta no catálogo de módulos consultado.
- Nenhuma instalação, atualização de módulo ou alteração de registros de negócio foi executada nessa validação. O login web pode registrar os metadados normais de autenticação do Odoo.
