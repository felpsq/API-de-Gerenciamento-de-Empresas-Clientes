from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from database import get_db
from models.produto import Produto
from models.fornecedor import Fornecedor
from models.categoria import Categoria
from schemas.produto import (
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoResponse,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def preparar_relacionamentos(dados, db):
    if dados.fornecedor_id is not None:
        if db.get(Fornecedor, dados.fornecedor_id) is None:
            raise HTTPException(404, "Fornecedor não encontrado")

    ids = dados.categoria_ids

    if len(ids) != len(set(ids)):
        raise HTTPException(422, "Categorias duplicadas")

    categorias = db.scalars(
        select(Categoria).where(Categoria.id.in_(ids))
    ).all()

    if len(categorias) != len(ids):
        raise HTTPException(404, "Uma ou mais categorias não existem")

    return categorias


def resposta_produto(produto):
    return {
        "id": produto.id,
        "nome": produto.nome,
        "codigo": produto.codigo,
        "preco_custo": produto.preco_custo,
        "preco_venda": produto.preco_venda,
        "quantidade_estoque": produto.quantidade_estoque,
        "data_cadastro": produto.data_cadastro,
        "fornecedor_id": produto.fornecedor_id,
        "categoria_ids": [c.id for c in produto.categorias],
    }


def consultar_produto(db, produto_id):
    return db.scalar(
        select(Produto)
        .options(selectinload(Produto.categorias))
        .where(Produto.id == produto_id)
    )


@router.post("", response_model=ProdutoResponse, status_code=201)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    categorias = preparar_relacionamentos(dados, db)

    valores = dados.model_dump(exclude={"categoria_ids"})
    produto = Produto(**valores)
    produto.categorias = categorias

    db.add(produto)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Código de produto já cadastrado")

    produto = consultar_produto(db, produto.id)
    return resposta_produto(produto)


@router.get("", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.scalars(
        select(Produto)
        .options(selectinload(Produto.categorias))
        .order_by(Produto.id)
    ).all()

    return [resposta_produto(p) for p in produtos]


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = consultar_produto(db, produto_id)

    if produto is None:
        raise HTTPException(404, "Produto não encontrado")

    return resposta_produto(produto)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
):
    produto = consultar_produto(db, produto_id)

    if produto is None:
        raise HTTPException(404, "Produto não encontrado")

    categorias = preparar_relacionamentos(dados, db)

    for campo, valor in dados.model_dump(
        exclude={"categoria_ids"}
    ).items():
        setattr(produto, campo, valor)

    produto.categorias = categorias

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Código de produto já cadastrado")

    produto = consultar_produto(db, produto_id)
    return resposta_produto(produto)


@router.delete("/{produto_id}", status_code=204)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = consultar_produto(db, produto_id)

    if produto is None:
        raise HTTPException(404, "Produto não encontrado")

    if produto.quantidade_estoque != 0:
        raise HTTPException(
            409,
            "Não é possível excluir produto com estoque"
        )

    db.delete(produto)
    db.commit()