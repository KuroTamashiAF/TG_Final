from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_qerry import (
    Paginator,
    orm_get_banner,
    orm_get_categories,
    orm_get_category_products,
)
from aiogram.types import InputMediaPhoto

from keyboards.inline_keyboard import (
    get_user_main_btns,
    user_catalog_btns,
    products_btns,
)


async def main_menu(session: AsyncSession, level: int, menu_name: str):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbrd = get_user_main_btns(level=level)

    return image, kbrd


async def catalog(session: AsyncSession, level: int, menu_name: str):
    banner = await orm_get_banner(session, menu_name)
    categories = await orm_get_categories(session)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbrd = user_catalog_btns(level=level, categories=categories)

    return image, kbrd


def pages(paginator: Paginator):
    btns = {}
    if paginator.has_previous():
        btns["⏮️ Пред"] = "previous"

    if paginator.has_next():
        btns["⏭️ След"] = "next"

    return btns


async def products(session: AsyncSession, level: int, category: int, page: int):
    products = await orm_get_category_products(session, category)

    paginator = Paginator(products, page=page)

    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}</strong>\n\
            {product.description}\n\
            Стоимость: {round(product.price),2}\n\
                <strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )
    paginator_btns = pages(paginator)

    kbds = products_btns(
        level=level,
        category=category,
        page=page,
        paginator_btns=paginator_btns,
        product_id=product.id,
    )
    return image, kbds


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    page: int | None = None,
    category: int | None = None,
):

    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
