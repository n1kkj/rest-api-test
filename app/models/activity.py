from typing import Optional, List

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_model import Base


organization_activity = sa.Table(
    'organization_activity',
    Base.metadata,
    sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id'), primary_key=True),
    sa.Column('activity_id', sa.Integer, sa.ForeignKey('activity.id'), primary_key=True),
)


class Activity(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(sa.Integer, ForeignKey('activity.id'), nullable=True)

    parent: Mapped[Optional['Activity']] = relationship(
        'Activity', remote_side=[id], back_populates='children', lazy='select'
    )

    children: Mapped[List['Activity']] = relationship(
        'Activity', back_populates='parent', cascade='all, delete-orphan', lazy='select'
    )

    organizations: Mapped[List['Organization']] = relationship(
        secondary=organization_activity, back_populates='activities', lazy='select'
    )
