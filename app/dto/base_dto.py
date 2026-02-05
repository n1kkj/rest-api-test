from pydantic import ConfigDict, BaseModel


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
