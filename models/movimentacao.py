from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_movimentacao_quantidade"),
        CheckConstraint(
            "tipo IN ('ENTRADA', 'SAIDA')",
            name="ck_movimentacao_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    data_movimentacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )