import pytest
from pydantic import ValidationError

from schemas.produto import ProdutoCreate
from schemas.movimentacao import MovimentacaoCreate


def test_produto_com_preco_negativo():
    with pytest.raises(ValidationError):
        ProdutoCreate(
            nome="Mouse",
            codigo="MOU-001",
            preco_custo="-10.00",
            preco_venda="50.00",
        )


def test_movimentacao_com_quantidade_zero():
    with pytest.raises(ValidationError):
        MovimentacaoCreate(
            produto_id=1,
            tipo="ENTRADA",
            quantidade=0,
        )


def test_movimentacao_com_tipo_invalido():
    with pytest.raises(ValidationError):
        MovimentacaoCreate(
            produto_id=1,
            tipo="TRANSFERENCIA",
            quantidade=10,
        )


def test_produto_valido():
    produto = ProdutoCreate(
        nome="Teclado",
        codigo="TEC-001",
        preco_custo="50.00",
        preco_venda="100.00",
    )

    assert produto.nome == "Teclado"
    assert produto.categoria_ids == []
    assert produto.fornecedor_id is None