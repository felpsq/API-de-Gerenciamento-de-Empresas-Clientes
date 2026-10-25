from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.produto import Produto
from models.movimentacao import Movimentacao
from schemas.movimentacao import (
    MovimentacaoCreate,
    MovimentacaoResponse,
    EstoqueResponse,
    TipoMovimentacao,
)

from datetime import datetime
from fastapi import Query
from sqlalchemy.orm import aliased

router = APIRouter(tags=["Estoque"])


@router.post(
    "/movimentacoes",
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimentacao(
    dados: MovimentacaoCreate,
    db: Session = Depends(get_db),
):
    try:
        # Bloqueia a linha do produto até a transação terminar.
        # Isso evita que duas saídas simultâneas utilizem o mesmo saldo.
        produto = db.scalar(
            select(Produto)
            .where(Produto.id == dados.produto_id)
            .with_for_update()
        )

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado",
            )

        if dados.tipo == TipoMovimentacao.ENTRADA:
            produto.quantidade_estoque += dados.quantidade

        else:
            if produto.quantidade_estoque < dados.quantidade:
                raise HTTPException(
                    status_code=409,
                    detail="Estoque insuficiente para a saída",
                )

            produto.quantidade_estoque -= dados.quantidade

        movimentacao = Movimentacao(
            produto_id=dados.produto_id,
            tipo=dados.tipo.value,
            quantidade=dados.quantidade,
        )

        db.add(movimentacao)

        # Saldo e histórico são gravados na mesma transação.
        # Se uma operação falhar, nenhuma das duas será confirmada.
        db.commit()
        db.refresh(movimentacao)

        return movimentacao

    except Exception:
        db.rollback()
        raise


@router.get(
    "/movimentacoes",
    response_model=list[MovimentacaoResponse],
)
def listar_movimentacoes(
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    fornecedor_id: int | None = None,
    db: Session = Depends(get_db),
):
    consulta = select(Movimentacao)

    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=422,
            detail="Data inicial não pode ser maior que a final"
        )

    if data_inicio:
        consulta = consulta.where(
            Movimentacao.data_movimentacao >= data_inicio
        )

    if data_fim:
        consulta = consulta.where(
            Movimentacao.data_movimentacao <= data_fim
        )

    if fornecedor_id is not None:
        consulta = consulta.join(
            Produto,
            Movimentacao.produto_id == Produto.id
        ).where(
            Produto.fornecedor_id == fornecedor_id
        )

    consulta = consulta.order_by(
        Movimentacao.data_movimentacao.desc(),
        Movimentacao.id.desc()
    )

    return db.scalars(consulta).all()


@router.get(
    "/produtos/{produto_id}/estoque",
    response_model=EstoqueResponse,
)
def consultar_estoque(
    produto_id: int,
    db: Session = Depends(get_db),
):
    produto = db.get(Produto, produto_id)

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    return {
        "produto_id": produto.id,
        "nome": produto.nome,
        "quantidade_estoque": produto.quantidade_estoque,
    }

@router.get(
    "/estoque/baixo",
    response_model=list[EstoqueResponse],
)
def listar_estoque_baixo(
    limite: int = Query(default=10, ge=0),
    db: Session = Depends(get_db),
):
    produtos = db.scalars(
        select(Produto)
        .where(Produto.quantidade_estoque <= limite)
        .order_by(Produto.quantidade_estoque, Produto.id)
    ).all()

    return [
        {
            "produto_id": produto.id,
            "nome": produto.nome,
            "quantidade_estoque": produto.quantidade_estoque,
        }
        for produto in produtos
    ]