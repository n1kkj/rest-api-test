from typing import Optional, List
from app.dto.base_dto import BaseDTO


class ActivitySimpleDTO(BaseDTO):
    id: int
    name: str
    parent_id: Optional[int] = None


class ActivityDTO(BaseDTO):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: Optional[List['ActivitySimpleDTO']] = None
    parent: Optional['ActivitySimpleDTO'] = None


class ActivityCreateDTO(BaseDTO):
    name: str
    parent_id: Optional[int] = None
