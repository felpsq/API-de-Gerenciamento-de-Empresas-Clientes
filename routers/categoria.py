from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.categoria import Categoria
from schemas.categoria import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse,
)

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_categoria(dados: CategoriaCreate, db: Session = Depends(get_db)):
    categoria = Categoria(**dados.model_dump())
    db.add(categoria)

    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Categoria já cadastrada"
        )

    return categoria


@router.get("", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.scalars(
        select(Categoria).order_by(Categoria.id)
    ).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada"
        )

    return categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int,
    dados: CategoriaUpdate,
    db: Session = Depends(get_db),
):
    categoria = db.get(Categoria, categoria_id)

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada"
        )

    for campo, valor in dados.model_dump().items():
        setattr(categoria, campo, valor)

    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Categoria já cadastrada"
        )

    return categoria


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
):
    categoria = db.get(Categoria, categoria_id)

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada"
        )

    db.delete(categoria)
    db.commit()