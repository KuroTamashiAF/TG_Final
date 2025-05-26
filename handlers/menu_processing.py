from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_qerry import (
    Paginator,
    orm_get_banner,
    orm_get_categories,
    orm_get_category_products,
    orm_delete_from_cart,
    orm_reduce_product_in_cart,
    orm_add_to_cart,
    orm_get_user_carts,
)
from aiogram.types import InputMediaPhoto
from aiogram import Bot  # TEST
from handlers.user_group import CHAT_ID_ORDERS  # TEST

from keyboards.inline_keyboard import (
    get_user_main_btns,
    user_catalog_btns,
    products_btns,
    get_btns_in_user_cart_products,
)

# from utils.order_creating import creating_order


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
            Стоимость: {round(product.price,2)}\n\
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


async def carts_menu(
    session: AsyncSession,
    level: int,
    menu_name: str,
    page: int,
    user_id: int,
    product_id: int,
):

    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "incremrnt":
        await orm_add_to_cart(session, user_id, product_id)

    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(
            media=banner.image, caption=f"<strong>{banner.description}</strong>"
        )
        kbds = get_btns_in_user_cart_products(
            level=level, page=None, paginator_btns=None, product_id=None
        )
    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price}$ x {cart.quantity} = {cart_price}$\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\nОбщая стоимость товаров в корзине {total_price}",
        )

        paginator_btns = pages(paginator)
        kbds = get_btns_in_user_cart_products(
            level=level,
            page=page,
            paginator_btns=paginator_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    page: int | None = None,
    category: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
):

    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts_menu(
            session,
            level,
            menu_name,
            page,
            user_id,
            product_id,
        )
