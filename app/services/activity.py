from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import logging

from app.dao.activity import ActivityDAO
from app.dto.activity import ActivityDTO

logger = logging.getLogger(__name__)


class ActivityService:
    @staticmethod
    async def get_activity_by_id(db: AsyncSession, activity_id: int) -> Optional[Dict[str, Any]]:
        """Получить вид деятельности по ID"""
        try:
            activity = await ActivityDAO.get_by_id(db, activity_id)
            return ActivityDTO.model_validate(activity).model_dump() if activity else None
        except Exception as e:
            logger.error(f'Error getting activity by id {activity_id}: {e}')
            raise

    @staticmethod
    async def get_root_activities(db: AsyncSession) -> List[Dict[str, Any]]:
        """Получить корневые виды деятельности"""
        try:
            activities = await ActivityDAO.get_root_activities(db)
            return [ActivityDTO.model_validate(act).model_dump() for act in activities]
        except Exception as e:
            logger.error(f'Error getting root activities: {e}')
            raise

    @staticmethod
    async def get_children_activities(db: AsyncSession, parent_id: int, max_depth: int = 3) -> List[ActivityDTO]:
        """Получить дочерние виды деятельности"""
        try:
            activities = await ActivityDAO.get_children(db, parent_id, max_depth)
            return [ActivityDTO.model_validate(act) for act in activities]
        except Exception as e:
            logger.error(f'Error getting children activities for parent {parent_id}: {e}')
            raise

    @staticmethod
    async def search_activities_by_name(db: AsyncSession, name: str) -> List[Dict[str, Any]]:
        """Поиск видов деятельности по названию"""
        try:
            activity = await ActivityDAO.get_by_name(db, name)
            return [ActivityDTO.model_validate(activity).model_dump()] if activity else []
        except Exception as e:
            logger.error(f'Error searching activities by name {name}: {e}')
            raise

    @staticmethod
    async def create_activity(db: AsyncSession, activity_data: Dict[str, Any]) -> ActivityDTO:
        """Создать новый вид деятельности"""
        try:
            activity = await ActivityDAO.create(db, activity_data)
            return ActivityDTO.model_validate(activity)
        except Exception as e:
            logger.error(f'Error creating activity: {e}')
            raise

    @staticmethod
    async def update_activity(
        db: AsyncSession, activity_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить вид деятельности"""
        try:
            activity = await ActivityDAO.update(db, activity_id, update_data)
            return ActivityDTO.model_validate(activity).model_dump() if activity else None
        except Exception as e:
            logger.error(f'Error updating activity {activity_id}: {e}')
            raise

    @staticmethod
    async def delete_activity(db: AsyncSession, activity_id: int) -> bool:
        """Удалить вид деятельности"""
        try:
            return await ActivityDAO.delete(db, activity_id)
        except Exception as e:
            logger.error(f'Error deleting activity {activity_id}: {e}')
            raise

    @staticmethod
    async def get_all_activities(db: AsyncSession) -> List[Dict[str, Any]]:
        """Получить все виды деятельности"""
        try:
            activities = await ActivityDAO.get_all(db)
            return [ActivityDTO.model_validate(act).model_dump() for act in activities]
        except Exception as e:
            logger.error(f'Error getting all activities: {e}')
            raise
