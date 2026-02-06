from typing import Optional, List, Any
from app.dto.base_dto import BaseDTO


class BuildingSimpleDTO(BaseDTO):
    id: int
    address: str
    latitude: float
    longitude: float


class BuildingDTO(BuildingSimpleDTO):
    pass


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
    organizations: List[Any]
