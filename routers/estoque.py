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
def listar_movimentacoes(db: Session = Depends(get_db)):
    return db.scalars(
        select(Movimentacao)
        .order_by(Movimentacao.id.desc())
    ).all()


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