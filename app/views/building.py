from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.database import get_db
from app.dto.building import BuildingDTO, BuildingCreateDTO, BuildingWithOrganizationsDTO, GeoQueryDTO
from app.services.building import BuildingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/buildings', tags=['buildings'])


@router.post('/', response_model=BuildingDTO, status_code=status.HTTP_201_CREATED, summary='Создать новое здание')
async def create_building(building_data: BuildingCreateDTO, db: AsyncSession = Depends(get_db)) -> BuildingDTO:
    """
    Создать новое здание.

    - **address**: Адрес здания
    - **latitude**: Широта
    - **longitude**: Долгота
    """
    try:
        building = await BuildingService.create_building(db, building_data.model_dump())
        return BuildingDTO(**building)
    except Exception as e:
        logger.error(f'Error creating building: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error creating building: {str(e)}'
        )


@router.get('/{building_id}', response_model=BuildingWithOrganizationsDTO, summary='Получить здание с организациями')
async def get_building(building_id: int, db: AsyncSession = Depends(get_db)) -> BuildingWithOrganizationsDTO:
    """
    Получить информацию о здании и список организаций в нём.
    """
    try:
        building = await BuildingService.get_building_with_organizations(db, building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f'Building with id {building_id} not found'
            )
        return BuildingWithOrganizationsDTO(**building)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error getting building {building_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting building: {str(e)}'
        )


@router.post('/geo/search', response_model=List[BuildingDTO], summary='Поиск зданий по геолокации')
async def search_buildings_by_geo(geo_query: GeoQueryDTO, db: AsyncSession = Depends(get_db)) -> List[BuildingDTO]:
    """
    Поиск зданий по геолокации.

    Варианты поиска:
    - В радиусе от точки: укажите latitude, longitude и radius_km
    - В прямоугольной области: укажите min_lat, max_lat, min_lng, max_lng
    """
    try:
        if geo_query.radius_km:
            buildings = await BuildingService.get_buildings_in_radius(
                db, geo_query.latitude, geo_query.longitude, geo_query.radius_km
            )
        elif all([geo_query.min_lat, geo_query.max_lat, geo_query.min_lng, geo_query.max_lng]):
            buildings = await BuildingService.get_buildings_in_rectangle(
                db, geo_query.min_lat, geo_query.max_lat, geo_query.min_lng, geo_query.max_lng
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Either radius_km or all rectangle coordinates must be provided',
            )

        return [BuildingDTO(**b) for b in buildings]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error searching buildings by geo: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error searching buildings: {str(e)}'
        )


@router.get('/', response_model=List[BuildingDTO], summary='Получить все здания')
async def get_all_buildings(db: AsyncSession = Depends(get_db)) -> List[BuildingDTO]:
    """
    Получить список всех зданий.
    """
    try:
        buildings = await BuildingService.get_all_buildings(db)
        return [BuildingDTO(**b) for b in buildings]
    except Exception as e:
        logger.error(f'Error getting all buildings: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error getting buildings: {str(e)}'
        )
