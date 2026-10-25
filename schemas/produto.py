from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    codigo: str = Field(min_length=1, max_length=50)
    preco_custo: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    preco_venda: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    fornecedor_id: int | None = None
    categoria_ids: list[int] = Field(default_factory=list)


class ProdutoUpdate(ProdutoCreate):
    pass


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    codigo: str
    preco_custo: Decimal
    preco_venda: Decimal
    quantidade_estoque: int
    data_cadastro: datetime
    fornecedor_id: int | None
    categoria_ids: list[int]

    model_config = ConfigDict(from_attributes=True)