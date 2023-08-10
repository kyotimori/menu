from typing import Optional
from pydantic import BaseModel, UUID4


class MenuBase(BaseModel):
    title: str
    description:str


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    pass


class MenuResponse(MenuBase):
    id: UUID4
    submenus_count: Optional[int]
    dishes_count: Optional[int]


class SubmenuBase(BaseModel):
    title: str
    description:str


class SubmenuCreate(SubmenuBase):
    pass


class SubmenuUpdate(SubmenuBase):
    pass


class SubmenuResponse(SubmenuBase):
    id: UUID4
    dishes_count: Optional[int]


class DishBase(BaseModel):
    title: str
    description: str
    price: str


class DishCreate(DishBase):
    pass


class DishUpdate(DishBase):
    pass


class DishResponse(DishBase):
    id: UUID4
