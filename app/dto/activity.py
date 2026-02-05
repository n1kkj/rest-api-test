from typing import Optional, List

from app.dto.base_dto import BaseDTO


class ActivityDTO(BaseDTO):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: Optional[List['ActivityDTO']] = None


class ActivityCreateDTO(BaseDTO):
    name: str
    parent_id: Optional[int] = None
