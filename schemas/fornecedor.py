from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FornecedorCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cnpj: str = Field(pattern=r"^\d{14}$")
    telefone: str = Field(min_length=1, max_length=20)
    email: EmailStr


class FornecedorUpdate(FornecedorCreate):
    pass


class FornecedorResponse(FornecedorCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)