from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.fornecedor import Fornecedor
from schemas.fornecedor import (
    FornecedorCreate,
    FornecedorUpdate,
    FornecedorResponse,
)

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


@router.post(
    "",
    response_model=FornecedorResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_fornecedor(dados: FornecedorCreate, db: Session = Depends(get_db)):
    fornecedor = Fornecedor(**dados.model_dump())

    db.add(fornecedor)

    try:
        db.commit()
        db.refresh(fornecedor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="CNPJ ou e-mail já cadastrado",
        )

    return fornecedor


@router.get("", response_model=list[FornecedorResponse])
def listar_fornecedores(db: Session = Depends(get_db)):
    return db.scalars(select(Fornecedor).order_by(Fornecedor.id)).all()


@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def buscar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)

    if fornecedor is None:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    return fornecedor


@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(
    fornecedor_id: int,
    dados: FornecedorUpdate,
    db: Session = Depends(get_db),
):
    fornecedor = db.get(Fornecedor, fornecedor_id)

    if fornecedor is None:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    for campo, valor in dados.model_dump().items():
        setattr(fornecedor, campo, valor)

    try:
        db.commit()
        db.refresh(fornecedor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="CNPJ ou e-mail já cadastrado",
        )

    return fornecedor


@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)

    if fornecedor is None:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    db.delete(fornecedor)
    db.commit()