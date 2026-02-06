from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import logging

from app.dao.organization import OrganizationDAO
from app.dto.organization import OrganizationDTO

logger = logging.getLogger(__name__)


class OrganizationService:
    @staticmethod
    async def get_organization_by_id(db: AsyncSession, organization_id: int) -> Optional[OrganizationDTO]:
        """Получить организацию по ID"""
        try:
            organization = await OrganizationDAO.get_by_id(db, organization_id)
            if not organization:
                return None
            return OrganizationDTO.model_validate(organization)
        except Exception as e:
            logger.error(f'Error getting organization by id {organization_id}: {e}')
            raise

    @staticmethod
    async def get_organizations_by_building(db: AsyncSession, building_id: int) -> List[OrganizationDTO]:
        """Получить все организации в здании"""
        try:
            organizations = await OrganizationDAO.get_by_building(db, building_id)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error getting organizations for building {building_id}: {e}')
            raise

    @staticmethod
    async def get_organizations_by_activity(db: AsyncSession, activity_id: int) -> List[OrganizationDTO]:
        """Получить организации по виду деятельности"""
        try:
            organizations = await OrganizationDAO.get_by_activity(db, activity_id)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error getting organizations for activity {activity_id}: {e}')
            raise

    @staticmethod
    async def search_organizations_by_name(db: AsyncSession, name: str) -> List[OrganizationDTO]:
        """Поиск организаций по названию"""
        try:
            organizations = await OrganizationDAO.get_by_name(db, name)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error searching organizations by name {name}: {e}')
            raise

    @staticmethod
    async def search_organizations_by_activity_tree(db: AsyncSession, activity_name: str) -> List[OrganizationDTO]:
        """Поиск организаций по дереву деятельности"""
        try:
            organizations = await OrganizationDAO.get_by_activities_tree(db, activity_name)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error searching organizations by activity tree {activity_name}: {e}')
            raise

    @staticmethod
    async def get_organizations_in_radius(
        db: AsyncSession, lat: float, lng: float, radius_km: float
    ) -> List[OrganizationDTO]:
        """Получить организации в радиусе"""
        try:
            organizations = await OrganizationDAO.get_in_radius(db, lat, lng, radius_km)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error getting organizations in radius {radius_km}km from ({lat}, {lng}): {e}')
            raise

    @staticmethod
    async def get_organizations_in_rectangle(
        db: AsyncSession, min_lat: float, max_lat: float, min_lng: float, max_lng: float
    ) -> List[OrganizationDTO]:
        """Получить организации в прямоугольной области"""
        try:
            organizations = await OrganizationDAO.get_in_rectangle(db, min_lat, max_lat, min_lng, max_lng)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error getting organizations in rectangle: {e}')
            raise

    @staticmethod
    async def create_organization(db: AsyncSession, organization_data: Dict[str, Any]) -> OrganizationDTO:
        """Создать новую организацию"""
        try:
            # Создаем организацию
            org_data = {'name': organization_data['name'], 'building_id': organization_data['building_id']}
            organization = await OrganizationDAO.create(db, org_data)

            # Добавляем телефоны
            for i, phone in enumerate(organization_data.get('phone_numbers', [])):
                is_primary = i == 0  # Первый телефон - основной
                await OrganizationDAO.add_phone(db, organization.id, phone, is_primary)

            # Добавляем виды деятельности
            for activity_id in organization_data.get('activity_ids', []):
                await OrganizationDAO.add_activity(db, organization.id, activity_id)

            return OrganizationDTO.model_validate(organization)
        except Exception as e:
            logger.error(f'Error creating organization: {e}')
            raise

    @staticmethod
    async def update_organization(
        db: AsyncSession, organization_id: int, update_data: Dict[str, Any]
    ) -> Optional[OrganizationDTO]:
        """Обновить организацию"""
        try:
            organization = await OrganizationDAO.update(db, organization_id, update_data)
            if not organization:
                return None
            return OrganizationDTO.model_validate(organization)
        except Exception as e:
            logger.error(f'Error updating organization {organization_id}: {e}')
            raise

    @staticmethod
    async def delete_organization(db: AsyncSession, organization_id: int) -> bool:
        """Удалить организацию"""
        try:
            return await OrganizationDAO.delete(db, organization_id)
        except Exception as e:
            logger.error(f'Error deleting organization {organization_id}: {e}')
            raise

    @staticmethod
    async def get_all_organizations(db: AsyncSession) -> List[OrganizationDTO]:
        """Получить все организации"""
        try:
            organizations = await OrganizationDAO.get_all(db)
            return [OrganizationDTO.model_validate(org) for org in organizations]
        except Exception as e:
            logger.error(f'Error getting all organizations: {e}')
            raise
