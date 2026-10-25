import uuid

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client(monkeypatch):
    # Impede executar os testes no banco principal por engano.
    import database

    if database.config.DB_NAME != "estoque_api_testes":
        pytest.fail("Configure DB_NAME=estoque_api_testes antes dos testes")

    with TestClient(app) as cliente:
        yield cliente


def test_fluxo_estoque(client):
    codigo = f"TEST-{uuid.uuid4().hex[:12]}"

    # Cria um produto com saldo inicial zero.
    resposta = client.post(
        "/produtos",
        json={
            "nome": "Produto de teste",
            "codigo": codigo,
            "preco_custo": "10.00",
            "preco_venda": "20.00",
            "fornecedor_id": None,
            "categoria_ids": [],
        },
    )

    assert resposta.status_code == 201, resposta.text

    produto_id = resposta.json()["id"]
    assert resposta.json()["quantidade_estoque"] == 0

    # Entrada de 20 unidades.
    resposta = client.post(
        "/movimentacoes",
        json={
            "produto_id": produto_id,
            "tipo": "ENTRADA",
            "quantidade": 20,
        },
    )

    assert resposta.status_code == 201, resposta.text

    # Saída de 5 unidades.
    resposta = client.post(
        "/movimentacoes",
        json={
            "produto_id": produto_id,
            "tipo": "SAIDA",
            "quantidade": 5,
        },
    )

    assert resposta.status_code == 201, resposta.text

    # Não permite retirar mais unidades que o saldo.
    resposta = client.post(
        "/movimentacoes",
        json={
            "produto_id": produto_id,
            "tipo": "SAIDA",
            "quantidade": 30,
        },
    )

    assert resposta.status_code == 409

    # A tentativa rejeitada não pode alterar o saldo.
    resposta = client.get(f"/produtos/{produto_id}/estoque")

    assert resposta.status_code == 200
    assert resposta.json()["quantidade_estoque"] == 15

    # Confere as duas movimentações registradas.
    resposta = client.get("/movimentacoes")

    assert resposta.status_code == 200

    historico = [
        m for m in resposta.json()
        if m["produto_id"] == produto_id
    ]

    assert len(historico) == 2

def test_erro_padronizado(client):
    resposta = client.get("/categorias/999999")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "erro": {
            "codigo": 404,
            "mensagem": "Categoria não encontrada",
        }
    }