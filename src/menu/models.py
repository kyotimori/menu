import uuid
from sqlalchemy import Column, String, ForeignKey, select, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, metadata


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, unique=True, nullable=False)
    description = Column(String)
    submenus = relationship('Submenu', back_populates='menu', cascade='all, delete')

    async def count_submenus(self, session: AsyncSession) -> int:
        query = select(func.count(Submenu.id)).filter(Submenu.menu_id == self.id)
        result = await session.execute(query)
        submenus_count = result.scalar()

        return submenus_count
    
    async def count_dishes(self, session: AsyncSession) -> int:
        query = select(func.count(Dish.id)).join(Submenu).filter(Submenu.menu_id == self.id)
        result = await session.execute(query)
        dishes_count = result.scalar()

        return dishes_count


class Submenu(Base):
    __tablename__ = 'submenu'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, unique=True, nullable=False)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menu.id'))
    menu = relationship('Menu', back_populates='submenus')
    dishes = relationship('Dish', back_populates='submenu', cascade='all, delete')

    async def count_dishes(self, session: AsyncSession): 
        query = select(func.count(Dish.id)).filter(Dish.submenu_id == self.id)
        result = await session.execute(query)
        dishes_count = result.scalar()

        return dishes_count


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, unique=True, nullable=False)
    description = Column(String)
    price = Column(String, nullable=False)
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenu.id'))
    submenu = relationship('Submenu', back_populates='dishes')
