from typing import Optional, List

from app.dto.base_dto import BaseDTO
from app.dto.organization import OrganizationBaseDTO


class BuildingDTO(BaseDTO):
    id: int
    address: str
    latitude: float
    longitude: float


class BuildingCreateDTO(BaseDTO):
    address: str
    latitude: float
    longitude: float


class GeoQueryDTO(BaseDTO):
    latitude: float
    longitude: float
    radius_km: Optional[float] = None
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lng: Optional[float] = None
    max_lng: Optional[float] = None


class BuildingWithOrganizationsDTO(BuildingDTO):
    organizations: List[OrganizationBaseDTO]
