from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Sequence
import math

from app.models.building import Building


class BuildingDAO:
    @classmethod
    async def get_by_id(cls, db: AsyncSession, building_id: int) -> Optional[Building]:
        query = select(Building).where(Building.id == building_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_address(cls, db: AsyncSession, address: str) -> Optional[Building]:
        query = select(Building).where(Building.address.ilike(f'%{address}%'))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence[Building]:
        query = select(Building)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_in_radius(cls, db: AsyncSession, lat: float, lng: float, radius_km: float) -> Sequence[Building]:
        lat_diff = radius_km / 111.0
        lng_diff = radius_km / (111.0 * abs(math.cos(math.radians(lat))))

        query = select(Building).where(
            and_(
                Building.latitude.between(lat - lat_diff, lat + lat_diff),
                Building.longitude.between(lng - lng_diff, lng + lng_diff),
            )
        )
        result = await db.execute(query)
        buildings = result.scalars().all()

        return [b for b in buildings if cls._calculate_distance(lat, lng, b.latitude, b.longitude) <= radius_km]

    @classmethod
    async def get_in_rectangle(
        cls, db: AsyncSession, min_lat: float, max_lat: float, min_lng: float, max_lng: float
    ) -> Sequence[Building]:
        query = select(Building).where(
            and_(Building.latitude.between(min_lat, max_lat), Building.longitude.between(min_lng, max_lng))
        )
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def create(cls, db: AsyncSession, building_data: dict) -> Building:
        building = Building(**building_data)
        db.add(building)
        await db.commit()
        await db.refresh(building)
        return building

    @classmethod
    async def update(cls, db: AsyncSession, building_id: int, update_data: dict) -> Optional[Building]:
        building = await cls.get_by_id(db, building_id)
        if building is None:
            return None

        for key, value in update_data.items():
            if hasattr(building, key):
                setattr(building, key, value)

        await db.commit()
        await db.refresh(building)
        return building

    @classmethod
    async def delete(cls, db: AsyncSession, building_id: int) -> bool:
        building = await cls.get_by_id(db, building_id)
        if building is None:
            return False

        await db.delete(building)
        await db.commit()
        return True

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
