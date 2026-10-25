from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)


class MovimentacaoResponse(MovimentacaoCreate):
    id: int
    data_movimentacao: datetime

    model_config = ConfigDict(from_attributes=True)


class EstoqueResponse(BaseModel):
    produto_id: int
    nome: str
    quantidade_estoque: int