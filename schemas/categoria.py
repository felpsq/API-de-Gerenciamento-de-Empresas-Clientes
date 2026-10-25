from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=255)


class CategoriaUpdate(CategoriaCreate):
    pass


class CategoriaResponse(CategoriaCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)