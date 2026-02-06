from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.database import get_db
from app.dto.activity import ActivityDTO, ActivityCreateDTO
from app.services.activity import ActivityService

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/activities', tags=['activities'])


@router.post(
    '/', response_model=ActivityDTO, status_code=status.HTTP_201_CREATED, summary='Создать новый вид деятельности'
)
async def create_activity(activity_data: ActivityCreateDTO, db: AsyncSession = Depends(get_db)) -> ActivityDTO:
    """
    Создать новый вид деятельности.

    - **name**: Название вида деятельности
    - **parent_id**: ID родительской деятельности (опционально)
    """
    try:
        activity = await ActivityService.create_activity(db, activity_data.model_dump())
        return activity
    except Exception as e:
        logger.error(f'Error creating activity: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error creating activity: {str(e)}'
        )


@router.get('/{activity_id}', response_model=ActivityDTO, summary='Получить вид деятельности по ID')
async def get_activity(activity_id: int, db: AsyncSession = Depends(get_db)) -> ActivityDTO:
    """
    Получить информацию о виде деятельности по ID.
    """
    try:
        activity = await ActivityService.get_activity_by_id(db, activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f'Activity with id {activity_id} not found'
            )
        return ActivityDTO(**activity)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error getting activity {activity_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting activity: {str(e)}'
        )


@router.get('/roots/root', response_model=List[ActivityDTO], summary='Получить корневые виды деятельности')
async def get_root_activities(db: AsyncSession = Depends(get_db)) -> List[ActivityDTO]:
    """
    Получить корневые виды деятельности.
    """
    try:
        activities = await ActivityService.get_root_activities(db)
        return [ActivityDTO(**act) for act in activities]
    except Exception as e:
        logger.error(f'Error getting root activities: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting activities: {str(e)}'
        )


@router.get('/{activity_id}/children', response_model=List[ActivityDTO], summary='Получить дочерние виды деятельности')
async def get_children_activities(
    activity_id: int,
    max_depth: int = Query(3, ge=1, le=3, description='Максимальная глубина вложенности (1-3)'),
    db: AsyncSession = Depends(get_db),
) -> List[ActivityDTO]:
    """
    Получить дочерние виды деятельности с ограничением глубины вложенности.
    По умолчанию глубина ограничена 3 уровнями.
    """
    try:
        activities = await ActivityService.get_children_activities(db, activity_id, max_depth)
        return activities
    except Exception as e:
        logger.error(f'Error getting children activities for {activity_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting activities: {str(e)}'
        )


@router.get('/search/by-name', response_model=List[ActivityDTO], summary='Поиск видов деятельности по названию')
async def search_activities_by_name(
    name: str = Query(..., description='Название вида деятельности для поиска'), db: AsyncSession = Depends(get_db)
) -> List[ActivityDTO]:
    """
    Поиск видов деятельности по названию (регистронезависимый поиск).
    """
    try:
        activities = await ActivityService.search_activities_by_name(db, name)
        return [ActivityDTO(**act) for act in activities]
    except Exception as e:
        logger.error(f'Error searching activities by name {name}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error searching activities: {str(e)}'
        )


@router.get('/', response_model=List[ActivityDTO], summary='Получить все виды деятельности')
async def get_all_activities(db: AsyncSession = Depends(get_db)) -> List[ActivityDTO]:
    """
    Получить список всех видов деятельности.
    """
    try:
        activities = await ActivityService.get_all_activities(db)
        return [ActivityDTO(**act) for act in activities]
    except Exception as e:
        logger.error(f'Error getting all activities: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting activities: {str(e)}'
        )
