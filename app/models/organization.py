from typing import List

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.activity import Activity, organization_activity
from app.models.base_model import Base
from app.models.building import Building


class OrganizationPhone(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        sa.Integer, ForeignKey('organization.id', ondelete='CASCADE'), nullable=False
    )
    phone_number: Mapped[str] = mapped_column(sa.String(50), nullable=False, index=True)
    organization: Mapped['Organization'] = relationship('Organization', back_populates='phones', lazy='select')


class Organization(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(sa.Integer, ForeignKey('building.id'), nullable=False)

    building: Mapped['Building'] = relationship('Building', back_populates='organizations', lazy='select')

    phones: Mapped[List['OrganizationPhone']] = relationship(
        'OrganizationPhone', back_populates='organization', cascade='all, delete-orphan', lazy='select'
    )

    activities: Mapped[List['Activity']] = relationship(
        secondary=organization_activity, back_populates='organizations', lazy='select'
    )
