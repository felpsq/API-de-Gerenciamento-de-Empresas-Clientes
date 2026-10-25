# API de Gerenciamento de Estoque

API REST desenvolvida para o desafio técnico Back-End da EcompJr — Prosel 2026.2. Permite gerenciar fornecedores, categorias e produtos, registrar entradas e saídas de estoque e consultar o histórico de movimentações.

## Tecnologias

- Python 3.13, FastAPI, Pydantic
- PostgreSQL, SQLAlchemy, driver `psycopg`
- Alembic para migrações
- Pytest e TestClient para testes

## Funcionalidades e regras de negócio

- CRUD de fornecedores, com CNPJ e e-mail únicos.
- CRUD de categorias, com nome único. Categorias associadas a produtos não podem ser excluídas (`409`).
- CRUD de produtos, com código/SKU único, fornecedor opcional e múltiplas categorias.
- O saldo de estoque é controlado por movimentações, não pelo cadastro/edição do produto.
- Entradas somam unidades; saídas subtraem unidades. Saídas que excedem o saldo retornam `409`.
- O registro da movimentação e a alteração do saldo são confirmados na mesma transação.
- O registro de movimentações utiliza `SELECT ... FOR UPDATE` na linha do produto para serializar atualizações concorrentes.
- Produtos com saldo diferente de zero ou histórico de movimentações não podem ser excluídos.
- Movimentações podem ser criadas e consultadas, mas não possuem rotas de edição/exclusão. A migração do projeto também deve manter a proteção de imutabilidade no banco.
- Consulta de produtos com estoque abaixo ou igual a um limite; filtro de movimentações por intervalo de data/hora e fornecedor.

## Instalação e execução

### Pré-requisitos

- Python 3.13 (ou versão compatível com as dependências)
- PostgreSQL em execução
- Git

### 1. Preparar ambiente

No PowerShell, na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configurar banco de dados

Crie um banco PostgreSQL, por exemplo `estoque_api`. Na raiz do projeto, crie um arquivo `.env` com:

```dotenv
DB_USER=postgres
DB_PASSWORD=SUA_SENHA
DB_HOST=localhost
DB_PORT=5432
DB_NAME=estoque_api
```

Substitua os valores pelos do seu ambiente. **Nunca publique `.env` ou credenciais no Git.** O projeto utiliza `pydantic-settings` para ler essas variáveis.

### 3. Aplicar migrações

```powershell
python -m alembic upgrade head
```

### 4. Iniciar a API

```powershell
python -m uvicorn main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- Especificação OpenAPI: http://127.0.0.1:8000/openapi.json

> O Swagger é gerado automaticamente pelos schemas Pydantic. Os exemplos abaixo descrevem as rotas verificadas nos arquivos do projeto. A descrição explícita de todos os erros no OpenAPI ainda deve ser revisada.

## Endpoints

### Fornecedores

| Método | Caminho | Sucesso | Erros relevantes |
|---|---|---|---|
| POST | `/fornecedores` | `201`, fornecedor criado | `409` CNPJ/e-mail duplicado; `422` validação |
| GET | `/fornecedores` | `200`, lista | `500` falha interna |
| GET | `/fornecedores/{fornecedor_id}` | `200`, objeto | `404` não encontrado |
| PUT | `/fornecedores/{fornecedor_id}` | `200`, objeto atualizado | `404`, `409`, `422` |
| DELETE | `/fornecedores/{fornecedor_id}` | `204`, sem corpo | `404`; conflitos de vínculo exigem revisão |

Exemplo de criação (`POST /fornecedores`):

```json
{
  "nome": "Distribuidora Exemplo",
  "cnpj": "12345678000195",
  "telefone": "75999999999",
  "email": "contato@exemplo.com"
}
```

Resposta de sucesso ilustrativa (`201`):

```json
{
  "id": 1,
  "nome": "Distribuidora Exemplo",
  "cnpj": "12345678000195",
  "telefone": "75999999999",
  "email": "contato@exemplo.com"
}
```

### Categorias

| Método | Caminho | Sucesso | Erros relevantes |
|---|---|---|---|
| POST | `/categorias` | `201`, categoria criada | `409` nome duplicado; `422` |
| GET | `/categorias` | `200`, lista | `500` |
| GET | `/categorias/{categoria_id}` | `200`, categoria | `404` |
| PUT | `/categorias/{categoria_id}` | `200`, categoria | `404`, `409`, `422` |
| DELETE | `/categorias/{categoria_id}` | `204`, sem corpo | `404`; `409` quando vinculada a produtos |

Exemplo (`POST /categorias`):

```json
{"nome": "Eletrônicos", "descricao": "Acessórios e dispositivos"}
```

Resposta ilustrativa (`201`):

```json
{"id": 1, "nome": "Eletrônicos", "descricao": "Acessórios e dispositivos"}
```

### Produtos

| Método | Caminho | Sucesso | Erros relevantes |
|---|---|---|---|
| POST | `/produtos` | `201`, produto criado | `404` fornecedor/categoria inexistente; `409` SKU duplicado; `422` |
| GET | `/produtos` | `200`, lista | `500` |
| GET | `/produtos/{produto_id}` | `200`, produto | `404` |
| PUT | `/produtos/{produto_id}` | `200`, produto atualizado | `404`, `409`, `422` |
| DELETE | `/produtos/{produto_id}` | `204`, sem corpo | `404`; `409` com saldo ou histórico |

Exemplo (`POST /produtos`):

```json
{
  "nome": "Mouse USB",
  "codigo": "MOU-001",
  "preco_custo": "25.00",
  "preco_venda": "49.90",
  "fornecedor_id": 1,
  "categoria_ids": [1]
}
```

`fornecedor_id` pode ser `null` e `categoria_ids` pode ser `[]`. Os IDs referenciados precisam existir. A resposta inclui também `id`, `quantidade_estoque` e `data_cadastro`. O saldo inicial é zero.

### Movimentações e consultas de estoque

| Método | Caminho | Sucesso | Erros relevantes |
|---|---|---|---|
| POST | `/movimentacoes` | `201`, movimentação registrada | `404` produto inexistente; `409` saldo insuficiente; `422` |
| GET | `/movimentacoes` | `200`, lista | `422` período inválido; `500` |
| GET | `/produtos/{produto_id}/estoque` | `200`, saldo | `404` |
| GET | `/estoque/baixo` | `200`, lista de saldos baixos | `422` limite negativo |

Exemplo de entrada (`POST /movimentacoes`):

```json
{"produto_id": 1, "tipo": "ENTRADA", "quantidade": 20}
```

Exemplo de saída:

```json
{"produto_id": 1, "tipo": "SAIDA", "quantidade": 5}
```

Resposta ilustrativa de criação (`201`):

```json
{
  "id": 1,
  "produto_id": 1,
  "tipo": "ENTRADA",
  "quantidade": 20,
  "data_movimentacao": "2026-10-25T03:00:00Z"
}
```

Saldo (`GET /produtos/1/estoque`):

```json
{"produto_id": 1, "nome": "Mouse USB", "quantidade_estoque": 15}
```

Estoque baixo: `GET /estoque/baixo?limite=10`. O parâmetro `limite` é inteiro não negativo e vale `10` por padrão. A resposta é uma lista de objetos com `produto_id`, `nome` e `quantidade_estoque`.

Filtros de histórico (todos opcionais):

- `data_inicio`: data/hora ISO 8601, inclusiva.
- `data_fim`: data/hora ISO 8601, inclusiva.
- `fornecedor_id`: ID do fornecedor vinculado ao produto.

Exemplo:

```http
GET /movimentacoes?data_inicio=2026-10-01T00:00:00Z&data_fim=2026-10-25T23:59:59Z&fornecedor_id=1
```

O filtro é aplicado sobre a data/hora da movimentação. Recomenda-se informar o fuso horário (`Z` ou offset). Um fornecedor sem movimentações associadas resulta em lista vazia.

## Formato de erros

A API utiliza handlers globais para apresentar erros de maneira padronizada:

**Recurso não encontrado (`404`):**

```json
{"erro": {"codigo": 404, "mensagem": "Produto não encontrado"}}
```

**Conflito (`409`):**

```json
{"erro": {"codigo": 409, "mensagem": "Estoque insuficiente para a saída"}}
```

**Validação (`422`):**

```json
{
  "erro": {
    "codigo": 422,
    "mensagem": "Dados inválidos na requisição",
    "detalhes": [
      {"campo": "body.quantidade", "mensagem": "Input should be greater than 0"}
    ]
  }
}
```

A mensagem específica de validação pode variar conforme a versão do Pydantic. Para falhas internas (`500`), a resposta informa `"Erro interno do servidor"` ou `"Erro interno ao acessar o banco de dados"`, sem expor o stack trace ao cliente. Logs técnicos permanecem no servidor.

## Testes automatizados

Os testes de validação não dependem de banco. O teste de integração exige um banco separado, chamado `estoque_api_testes`.

No PostgreSQL, crie `estoque_api_testes`. No PowerShell:

```powershell
$env:DB_NAME="estoque_api_testes"
python -m alembic upgrade head
python -m pytest -v
Remove-Item Env:DB_NAME
```

**Atenção:** não execute os testes de integração apontando para o banco principal. O teste de fluxo cria registros no banco de testes.

Os testes existentes cobrem validação de preços e movimentações, fluxo de entrada/saída, rejeição de saída acima do saldo e formato de erro `404`. Eles não constituem cobertura integral de todas as rotas.

## Estrutura do projeto

```text
.
├── main.py                 # Instância FastAPI e inclusão das rotas
├── database.py             # Configuração PostgreSQL e sessões SQLAlchemy
├── handlers.py             # Tratamento global de exceções
├── models/                 # Entidades e relacionamentos ORM
├── schemas/                # Validação e serialização Pydantic
├── routers/                # Endpoints REST
├── alembic/                # Migrações do banco
├── tests/                  # Testes automatizados
├── alembic.ini
├── requirements.txt
└── .env                    # Configuração local, não versionada
```

## Decisões técnicas

**Transações atômicas:** o saldo e o histórico de uma movimentação são gravados juntos. Se houver falha, a transação sofre rollback, evitando saldo atualizado sem registro correspondente.

**Concorrência:** o bloqueio de linha com `SELECT ... FOR UPDATE` impede que duas transações de movimentação leiam e alterem simultaneamente o mesmo saldo desatualizado. Isso depende do uso do PostgreSQL e de todas as movimentações seguirem o mesmo fluxo transacional.

**Auditoria:** a API não disponibiliza PUT/PATCH/DELETE para movimentações. O histórico de um produto impede sua exclusão. A proteção adicional por trigger deve permanecer nas migrações aplicadas.

**Separação de responsabilidades:** `models` define a persistência, `schemas` valida os dados, `routers` implementa a lógica HTTP, `database.py` fornece sessões e `handlers.py` padroniza erros.

## Histórico de desenvolvimento

O projeto adota **Conventional Commits** (`feat:`, `fix:`, `test:`, `docs:` etc.) para facilitar o acompanhamento das mudanças.
