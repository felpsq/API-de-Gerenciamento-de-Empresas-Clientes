from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )