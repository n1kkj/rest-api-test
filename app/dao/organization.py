from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence

from app.dao.activity import ActivityDAO
from app.dao.building import BuildingDAO
from app.models.activity import organization_activity, Activity
from app.models.organization import Organization, OrganizationPhone


class OrganizationDAO:
    @classmethod
    async def get_by_id(cls, db: AsyncSession, organization_id: int) -> Optional[Organization]:
        query = select(Organization).where(Organization.id == organization_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str) -> Sequence[Organization]:
        query = select(Organization).where(Organization.name.ilike(f'%{name}%'))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_building(cls, db: AsyncSession, building_id: int) -> Sequence[Organization]:
        query = select(Organization).where(Organization.building_id == building_id)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_activity(cls, db: AsyncSession, activity_id: int) -> Sequence[Organization]:
        activity_ids = await ActivityDAO.get_all_children_ids(db, activity_id)

        query = (
            select(Organization)
            .join(organization_activity, Organization.id == organization_activity.c.organization_id)
            .where(organization_activity.c.activity_id.in_(activity_ids))
            .distinct()
        )

        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_activities_tree(cls, db: AsyncSession, activity_name: str) -> Sequence[Organization]:
        query = select(Activity).where(Activity.name.ilike(f'%{activity_name}%'))
        result = await db.execute(query)
        activities = result.scalars().all()

        if not activities:
            return []

        all_organizations = []
        for activity in activities:
            organizations = await cls.get_by_activity(db, activity.id)
            all_organizations.extend(org for org in organizations if org not in all_organizations)

        return all_organizations

    @classmethod
    async def get_in_radius(cls, db: AsyncSession, lat: float, lng: float, radius_km: float) -> Sequence[Organization]:
        buildings = await BuildingDAO.get_in_radius(db, lat, lng, radius_km)
        building_ids = [b.id for b in buildings]

        if not building_ids:
            return []

        query = select(Organization).where(Organization.building_id.in_(building_ids))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_in_rectangle(
        cls, db: AsyncSession, min_lat: float, max_lat: float, min_lng: float, max_lng: float
    ) -> Sequence[Organization]:
        buildings = await BuildingDAO.get_in_rectangle(db, min_lat, max_lat, min_lng, max_lng)
        building_ids = [b.id for b in buildings]

        if not building_ids:
            return []

        query = select(Organization).where(Organization.building_id.in_(building_ids))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence[Organization]:
        query = select(Organization)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def create(cls, db: AsyncSession, organization_data: dict) -> Organization:
        organization = Organization(**organization_data)
        db.add(organization)
        await db.commit()
        await db.refresh(organization)
        return organization

    @classmethod
    async def update(cls, db: AsyncSession, organization_id: int, update_data: dict) -> Optional[Organization]:
        organization = await cls.get_by_id(db, organization_id)
        if organization is None:
            return None

        for key, value in update_data.items():
            if hasattr(organization, key):
                setattr(organization, key, value)

        await db.commit()
        await db.refresh(organization)
        return organization

    @classmethod
    async def delete(cls, db: AsyncSession, organization_id: int) -> bool:
        organization = await cls.get_by_id(db, organization_id)
        if organization is None:
            return False

        await db.delete(organization)
        await db.commit()
        return True

    @classmethod
    async def add_phone(
        cls, db: AsyncSession, organization_id: int, phone_number: str, is_primary: bool = False
    ) -> OrganizationPhone:
        phone = OrganizationPhone(
            organization_id=organization_id,
            phone_number=phone_number,
        )
        db.add(phone)
        await db.commit()
        await db.refresh(phone)
        return phone

    @classmethod
    async def add_activity(cls, db: AsyncSession, organization_id: int, activity_id: int) -> None:
        query = organization_activity.insert().values(organization_id=organization_id, activity_id=activity_id)
        await db.execute(query)
        await db.commit()
