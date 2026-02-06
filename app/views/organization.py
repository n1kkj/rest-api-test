from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.database import get_db
from app.dto.building import GeoQueryDTO
from app.dto.organization import OrganizationCreateDTO, OrganizationDTO, OrganizationUpdateDTO
from app.services.organization import OrganizationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/organizations', tags=['organizations'])


@router.post(
    '/', response_model=OrganizationDTO, status_code=status.HTTP_201_CREATED, summary='Создать новую организацию'
)
async def create_organization(
    organization_data: OrganizationCreateDTO, db: AsyncSession = Depends(get_db)
) -> OrganizationDTO:
    """
    Создать новую организацию.

    - **name**: Название организации
    - **building_id**: ID здания
    - **phone_numbers**: Список номеров телефонов
    - **activity_ids**: Список ID видов деятельности
    """
    try:
        organization = await OrganizationService.create_organization(db, organization_data.model_dump())
        return organization
    except Exception as e:
        logger.error(f'Error creating organization: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error creating organization: {str(e)}'
        )


@router.get('/{organization_id}', response_model=OrganizationDTO, summary='Получить организацию по ID')
async def get_organization(organization_id: int, db: AsyncSession = Depends(get_db)) -> OrganizationDTO:
    """
    Получить подробную информацию об организации по её идентификатору.
    """
    try:
        organization = await OrganizationService.get_organization_by_id(db, organization_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f'Organization with id {organization_id} not found'
            )
        return organization
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error getting organization {organization_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting organization: {str(e)}'
        )


@router.get('/building/{building_id}', response_model=List[OrganizationDTO], summary='Список организаций в здании')
async def get_organizations_by_building(building_id: int, db: AsyncSession = Depends(get_db)) -> List[OrganizationDTO]:
    """
    Получить список всех организаций, находящихся в конкретном здании.
    """
    try:
        organizations = await OrganizationService.get_organizations_by_building(db, building_id)
        return organizations
    except Exception as e:
        logger.error(f'Error getting organizations for building {building_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting organizations: {str(e)}'
        )


@router.get(
    '/activity/{activity_id}', response_model=List[OrganizationDTO], summary='Список организаций по виду деятельности'
)
async def get_organizations_by_activity(activity_id: int, db: AsyncSession = Depends(get_db)) -> List[OrganizationDTO]:
    """
    Получить список всех организаций, которые относятся к указанному виду деятельности.
    Включает организации с дочерними видами деятельности.
    """
    try:
        organizations = await OrganizationService.get_organizations_by_activity(db, activity_id)
        return organizations
    except Exception as e:
        logger.error(f'Error getting organizations for activity {activity_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting organizations: {str(e)}'
        )


@router.post('/geo/search', response_model=List[OrganizationDTO], summary='Поиск организаций по геолокации')
async def search_organizations_by_geo(
    geo_query: GeoQueryDTO, db: AsyncSession = Depends(get_db)
) -> List[OrganizationDTO]:
    """
    Поиск организаций по геолокации.

    Варианты поиска:
    - В радиусе от точки: укажите latitude, longitude и radius_km
    - В прямоугольной области: укажите min_lat, max_lat, min_lng, max_lng
    """
    try:
        if geo_query.radius_km:
            organizations = await OrganizationService.get_organizations_in_radius(
                db, geo_query.latitude, geo_query.longitude, geo_query.radius_km
            )
        elif all([geo_query.min_lat, geo_query.max_lat, geo_query.min_lng, geo_query.max_lng]):
            organizations = await OrganizationService.get_organizations_in_rectangle(
                db, geo_query.min_lat, geo_query.max_lat, geo_query.min_lng, geo_query.max_lng
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Either radius_km or all rectangle coordinates must be provided',
            )

        return organizations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error searching organizations by geo: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error searching organizations: {str(e)}'
        )


@router.get('/search/by-name', response_model=List[OrganizationDTO], summary='Поиск организаций по названию')
async def search_organizations_by_name(
    name: str = Query(..., description='Название организации для поиска'), db: AsyncSession = Depends(get_db)
) -> List[OrganizationDTO]:
    """
    Поиск организации по названию (регистронезависимый поиск).
    """
    try:
        organizations = await OrganizationService.search_organizations_by_name(db, name)
        return organizations
    except Exception as e:
        logger.error(f'Error searching organizations by name {name}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error searching organizations: {str(e)}'
        )


@router.get(
    '/search/by-activity-tree', response_model=List[OrganizationDTO], summary='Поиск организаций по дереву деятельности'
)
async def search_organizations_by_activity_tree(
    activity_name: str = Query(..., description='Название вида деятельности для поиска'),
    db: AsyncSession = Depends(get_db),
) -> List[OrganizationDTO]:
    """
    Поиск организаций по дереву деятельности.

    Пример: поиск по "Еда" найдет организации с видами деятельности:
    - Еда (корневой уровень)
    - Мясная продукция (дочерний уровень)
    - Молочная продукция (дочерний уровень)
    и т.д. (до 3 уровней вложенности)
    """
    try:
        organizations = await OrganizationService.search_organizations_by_activity_tree(db, activity_name)
        return organizations
    except Exception as e:
        logger.error(f'Error searching organizations by activity tree {activity_name}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error searching organizations: {str(e)}'
        )


@router.get('/', response_model=List[OrganizationDTO], summary='Получить все организации')
async def get_all_organizations(db: AsyncSession = Depends(get_db)) -> List[OrganizationDTO]:
    """
    Получить список всех организаций.
    """
    try:
        organizations = await OrganizationService.get_all_organizations(db)
        return organizations
    except Exception as e:
        logger.error(f'Error getting all organizations: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting organizations: {str(e)}'
        )


@router.put('/{organization_id}', response_model=OrganizationDTO, summary='Обновить организацию')
async def update_organization(
    organization_id: int, update_data: OrganizationUpdateDTO, db: AsyncSession = Depends(get_db)
) -> OrganizationDTO:
    """
    Обновить информацию об организации.
    """
    try:
        organization = await OrganizationService.update_organization(
            db, organization_id, update_data.model_dump(exclude_unset=True)
        )
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f'Organization with id {organization_id} not found'
            )
        return organization
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error updating organization {organization_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error updating organization: {str(e)}'
        )


@router.delete('/{organization_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Удалить организацию')
async def delete_organization(organization_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить организацию по ID.
    """
    try:
        success = await OrganizationService.delete_organization(db, organization_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f'Organization with id {organization_id} not found'
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error deleting organization {organization_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error deleting organization: {str(e)}'
        )
