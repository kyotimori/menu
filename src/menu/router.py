from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload

from database import get_async_session
from menu.models import Menu, Submenu, Dish
from menu.schemas import MenuCreate, MenuResponse, MenuUpdate, SubmenuCreate, SubmenuUpdate, DishCreate, DishUpdate, DishResponse


router = APIRouter(
    prefix='/api/v1/menus',
    tags=['Menu']
) 


@router.get('/')
async def get_menu_list(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu)
    result = await session.execute(query)

    return result.scalars().all()


@router.get('/{menu_id}', response_model=MenuResponse)
async def get_menu(menu_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).filter(Menu.id == menu_id)
    result = await session.execute(query)
    menu = result.scalar() 
    if not menu:
        raise HTTPException(status_code=404, detail='menu not found')
    
    submenus_count = await menu.count_submenus(session)
    dishes_count = await menu.count_dishes(session)

    menu_data = menu.__dict__
    menu_data['submenus_count'] = submenus_count
    menu_data['dishes_count'] = dishes_count

    return menu_data
    
    
@router.post('/')
async def add_menu(new_menu: MenuCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Menu).values(**new_menu.dict())
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content=new_menu.dict(), status_code=201)


@router.patch('/{menu_id}')
async def update_menu(menu_id: UUID4, updated_menu: MenuUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).filter(Menu.id == menu_id)
    result = await session.execute(query)
    menu = result.scalar()

    if not menu:
        raise HTTPException(status_code=404, detail='menu not found')
    
    for field, value in updated_menu.dict().items():
        setattr(menu, field, value)

    await session.commit()
    
    return menu


@router.delete('/{menu_id}')
async def delete_menu(menu_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).filter(Menu.id == menu_id)
    result = await session.execute(query)
    menu = result.scalar()

    if not menu:
        raise HTTPException(status_code=404, detail='menu not found')
    
    await session.delete(menu)
    await session.commit()

    return {'message': 'Menu deleted successfully'}


@router.get('/{menu_id}/submenus')
async def get_submenus_list(menu_id: str, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).options(joinedload(Menu.submenus)).filter(Menu.id == menu_id)
    result = await session.execute(query)
    menu = result.scalar()

    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    return menu.submenus

@router.post('/{menu_id}/submenus')
async def add_submenu(menu_id: UUID4, new_submenu: SubmenuCreate, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).filter(Menu.id == menu_id)
    result = await session.execute(query)
    menu = result.scalar()

    if not menu:
        raise HTTPException(status_code=404, detail="menu not found")

    submenu_data = new_submenu.dict()
    submenu_data["menu_id"] = menu.id
    submenu = Submenu(**submenu_data)

    session.add(submenu)
    await session.commit()

    return JSONResponse(content=new_submenu.dict(), status_code=201)


@router.get('/{menu_id}/submenus/{submenu_id}')
async def get_submenu(menu_id: UUID4, submenu_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).filter(Submenu.id == submenu_id and Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenu = result.scalar()

    if not submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    
    dishes_count = await submenu.count_dishes(session)
    
    submenu_data = submenu.__dict__
    submenu_data['dishes_count'] = dishes_count
    
    return submenu_data    


@router.patch('/{menu_id}/submenus/{submenu_id}')
async def add_submenu(menu_id: UUID4, submenu_id: UUID4, updated_submenu: SubmenuUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).filter(Submenu.id == submenu_id and Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenu = result.scalar()

    if not submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    
    for field, values in updated_submenu.dict().items():
        setattr(submenu, field, values)

    await session.commit()

    return submenu


@router.delete('/{menu_id}/submenus/{submenu_id}')
async def add_submenu(menu_id: UUID4, submenu_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).filter(Submenu.id == submenu_id and Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenu = result.scalar()

    if not submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    
    await session.delete(submenu)
    await session.commit()

    return {'message': 'Submenu deleted successfully'}


@router.get('/{menu_id}/submenus/{submenu_id}/dishes')
async def get_dishes_list(menu_id: UUID4, submenu_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).options(joinedload(Submenu.dishes)).filter(Submenu.id == submenu_id and Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenu = result.scalar()

    if not submenu:
        raise HTTPException(status_code=404, detail='submenu not found')
    
    return submenu.dishes


@router.post('/{menu_id}/submenus/{submenu_id}/dishes')
async def add_dish(menu_id: UUID4, submenu_id: UUID4, new_dish: DishCreate, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).filter(Submenu.id == submenu_id and Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenu = result.scalar()

    if not submenu:
        raise HTTPException(status_code=404, detail='submenu not found')
    
    dish_data = new_dish.dict()
    dish_data['submenu_id'] = submenu.id
    dish = Dish(**dish_data)

    session.add(dish)
    await session.commit()

    return JSONResponse(content=new_dish.dict(), status_code=201)


@router.get('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishResponse)
async def get_dish(menu_id: UUID4, submenu_id: UUID4, dish_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).filter(Dish.id == dish_id and Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    dish = result.scalar()

    if not dish:
        raise HTTPException(status_code=404, detail='dish not found')
    
    return dish


@router.patch('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def update_dish(menu_id: UUID4, submenu_id: UUID4, dish_id: UUID4, updated_dish: DishUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).filter(Dish.id == dish_id and Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    dish = result.scalar()

    if not dish:
        raise HTTPException(status_code=404, detail='dish not found')
    
    for fiels, value in updated_dish.dict().items():
        setattr(dish, fiels, value)

    await session.commit()

    return dish


@router.delete('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def update_dish(menu_id: UUID4, submenu_id: UUID4, dish_id: UUID4, session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).filter(Dish.id == dish_id and Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    dish = result.scalar()

    if not dish:
        raise HTTPException(status_code=404, detail='dish not found')
    
    await session.delete(dish)
    await session.commit()
    
    return {'message': 'Dish deleted successfully'}
