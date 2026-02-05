from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_model import Base


class Building(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(sa.String(500), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(sa.Float, nullable=False)
    longitude: Mapped[float] = mapped_column(sa.Float, nullable=False)

    organizations: Mapped[List['Organization']] = relationship(
        'Organization', back_populates='building', cascade='all, delete-orphan', lazy='select'
    )
