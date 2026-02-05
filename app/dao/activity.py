from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, Sequence, List

from app.models.activity import Activity


class ActivityDAO:
    @classmethod
    async def get_by_id(cls, db: AsyncSession, activity_id: int) -> Optional[Activity]:
        query = select(Activity).where(Activity.id == activity_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str) -> Optional[Activity]:
        query = select(Activity).where(Activity.name.ilike(f'%{name}%'))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence[Activity]:
        query = select(Activity)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_root_activities(cls, db: AsyncSession) -> Sequence[Activity]:
        """Получить корневые виды деятельности (без родителя)"""
        query = select(Activity).where(Activity.parent_id.is_(None))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_children(cls, db: AsyncSession, parent_id: int, max_depth: int = 3) -> Sequence[Activity]:
        """Получить дочерние виды деятельности с ограничением глубины"""
        from sqlalchemy.orm import aliased

        Activity1 = aliased(Activity)
        Activity2 = aliased(Activity)
        Activity3 = aliased(Activity)

        if max_depth == 1:
            query = select(Activity).where(Activity.parent_id == parent_id)
        elif max_depth == 2:
            query = select(Activity).where(
                or_(
                    Activity.parent_id == parent_id,
                    Activity.parent_id.in_(select(Activity1.id).where(Activity1.parent_id == parent_id)),
                )
            )
        else:  # max_depth == 3
            query = select(Activity).where(
                or_(
                    Activity.parent_id == parent_id,
                    Activity.parent_id.in_(select(Activity1.id).where(Activity1.parent_id == parent_id)),
                    Activity.parent_id.in_(
                        select(Activity2.id).where(
                            Activity2.parent_id.in_(select(Activity3.id).where(Activity3.parent_id == parent_id))
                        )
                    ),
                )
            )

        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all_children_ids(cls, db: AsyncSession, activity_id: int, max_depth: int = 3) -> List[int]:
        activities = await cls.get_children(db, activity_id, max_depth)
        return [activity.id for activity in activities] + [activity_id]

    @classmethod
    async def create(cls, db: AsyncSession, activity_data: dict) -> Activity:
        activity = Activity(**activity_data)
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return activity

    @classmethod
    async def update(cls, db: AsyncSession, activity_id: int, update_data: dict) -> Optional[Activity]:
        activity = await cls.get_by_id(db, activity_id)
        if activity is None:
            return None

        for key, value in update_data.items():
            if hasattr(activity, key):
                setattr(activity, key, value)

        await db.commit()
        await db.refresh(activity)
        return activity

    @classmethod
    async def delete(cls, db: AsyncSession, activity_id: int) -> bool:
        activity = await cls.get_by_id(db, activity_id)
        if activity is None:
            return False

        await db.delete(activity)
        await db.commit()
        return True
