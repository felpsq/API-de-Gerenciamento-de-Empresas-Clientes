from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer,
    Numeric, String, Table
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


produto_categoria = Table(
    "produto_categoria",
    Base.metadata,
    Column(
        "produto_id",
        ForeignKey("produtos.id"),
        primary_key=True
    ),
    Column(
        "categoria_id",
        ForeignKey("categorias.id"),
        primary_key=True
    ),
)


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    codigo: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    preco_custo: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    preco_venda: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    quantidade_estoque: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    fornecedor_id: Mapped[int | None] = mapped_column(
        ForeignKey("fornecedores.id"),
        nullable=True
    )

    fornecedor = relationship("Fornecedor")

    categorias = relationship(
        "Categoria",
        secondary=produto_categoria
    )