from typing import Optional, List

from app.dto.activity import ActivityDTO
from app.dto.base_dto import BaseDTO
from app.dto.building import BuildingDTO


class PhoneDTO(BaseDTO):
    id: int
    phone_number: str


class OrganizationBaseDTO(BaseDTO):
    id: int
    name: str
    building_id: int


class OrganizationCreateDTO(BaseDTO):
    name: str
    building_id: int
    phone_numbers: List[str]
    activity_ids: List[int]


class OrganizationUpdateDTO(BaseDTO):
    name: Optional[str] = None
    building_id: Optional[int] = None
    phone_numbers: Optional[List[str]] = None
    activity_ids: Optional[List[int]] = None


class OrganizationDTO(OrganizationBaseDTO):
    building: BuildingDTO
    phones: List[PhoneDTO]
    activities: List[ActivityDTO]


class OrganizationDetailDTO(OrganizationBaseDTO):
    building: BuildingDTO
    phones: List[PhoneDTO]
    activities: List[ActivityDTO]
