from pydantic import BaseModel, ConfigDict, Field


class PartCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)


class PartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    quantity: int


class OrderCreate(BaseModel):
    part_id: int
    quantity: int = Field(gt=0)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    part_id: int
    part_name: str
    quantity: int
    status: str
    machine: str | None