from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import logging

from app.dao.building import BuildingDAO
from app.dao.organization import OrganizationDAO
from app.dto.building import BuildingDTO
from app.dto.organization import OrganizationBaseDTO

logger = logging.getLogger(__name__)


class BuildingService:
    @staticmethod
    async def get_building_by_id(db: AsyncSession, building_id: int) -> Optional[Dict[str, Any]]:
        """Получить здание по ID"""
        try:
            building = await BuildingDAO.get_by_id(db, building_id)
            return BuildingDTO.model_validate(building).model_dump() if building else None
        except Exception as e:
            logger.error(f'Error getting building by id {building_id}: {e}')
            raise

    @staticmethod
    async def get_buildings_in_radius(
        db: AsyncSession, lat: float, lng: float, radius_km: float
    ) -> List[Dict[str, Any]]:
        """Получить здания в радиусе"""
        try:
            buildings = await BuildingDAO.get_in_radius(db, lat, lng, radius_km)
            return [BuildingDTO.model_validate(b).model_dump() for b in buildings]
        except Exception as e:
            logger.error(f'Error getting buildings in radius {radius_km}km from ({lat}, {lng}): {e}')
            raise

    @staticmethod
    async def get_buildings_in_rectangle(
        db: AsyncSession, min_lat: float, max_lat: float, min_lng: float, max_lng: float
    ) -> List[Dict[str, Any]]:
        """Получить здания в прямоугольной области"""
        try:
            buildings = await BuildingDAO.get_in_rectangle(db, min_lat, max_lat, min_lng, max_lng)
            return [BuildingDTO.model_validate(b).model_dump() for b in buildings]
        except Exception as e:
            logger.error(f'Error getting buildings in rectangle: {e}')
            raise

    @staticmethod
    async def get_building_with_organizations(db: AsyncSession, building_id: int) -> Optional[Dict[str, Any]]:
        """Получить здание с организациями"""
        try:
            building = await BuildingDAO.get_by_id(db, building_id)
            if not building:
                return None

            organizations = await OrganizationDAO.get_by_building(db, building_id)

            result = BuildingDTO.model_validate(building).model_dump()
            result['organizations'] = [OrganizationBaseDTO.model_validate(org).model_dump() for org in organizations]

            return result
        except Exception as e:
            logger.error(f'Error getting building with organizations {building_id}: {e}')
            raise

    @staticmethod
    async def create_building(db: AsyncSession, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новое здание"""
        try:
            building = await BuildingDAO.create(db, building_data)
            return BuildingDTO.model_validate(building).model_dump()
        except Exception as e:
            logger.error(f'Error creating building: {e}')
            raise

    @staticmethod
    async def update_building(
        db: AsyncSession, building_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить здание"""
        try:
            building = await BuildingDAO.update(db, building_id, update_data)
            return BuildingDTO.model_validate(building).model_dump() if building else None
        except Exception as e:
            logger.error(f'Error updating building {building_id}: {e}')
            raise

    @staticmethod
    async def delete_building(db: AsyncSession, building_id: int) -> bool:
        """Удалить здание"""
        try:
            return await BuildingDAO.delete(db, building_id)
        except Exception as e:
            logger.error(f'Error deleting building {building_id}: {e}')
            raise

    @staticmethod
    async def get_all_buildings(db: AsyncSession) -> List[Dict[str, Any]]:
        """Получить все здания"""
        try:
            buildings = await BuildingDAO.get_all(db)
            return [BuildingDTO.model_validate(b).model_dump() for b in buildings]
        except Exception as e:
            logger.error(f'Error getting all buildings: {e}')
            raise
