from aiogram import types, Router, F
from aiogram.filters import CommandStart
import aiofiles
from filters.chat_types import ChatTypeFilter

from sqlalchemy.ext.asyncio import AsyncSession
from handlers.menu_processing import get_menu_content
from keyboards.inline_keyboard import MenuCallBack
from database.orm_qerry import orm_add_user, orm_add_to_cart
from utils.order_creating import creating_order


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


async def add_to_cart(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    user = callback.from_user           # Добавить принты и посмотреть что и как записываеься
    await orm_add_user(
        session=session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(
        session=session, user_id=user.id, product_id=callback_data.product_id
    )
    await callback.answer("Товар добавлен в корзину")


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
    callback: types.CallbackQuery,
    callback_data: MenuCallBack,
    session: AsyncSession,
):
    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_private_router.callback_query(F.data == "order_callback")
async def orderd(callback: types.CallbackQuery, session: AsyncSession):
    admins_list = callback.bot.my_admins_list
    user_id = callback.from_user.id
    order_str = await creating_order(
        user_id=user_id, callback=callback, session=session
    )

    for id_admins in admins_list:  # [780962046, 8097195782, 1506212028]
        if id_admins != 8097195782:
            await callback.bot.send_message(chat_id=id_admins, text=order_str)
    await callback.answer(text="Заказ оформлен мы с вами свяжимся позже")
