from aiogram import types, Router, F
from aiogram.filters import CommandStart
import aiofiles
from filters.chat_types import ChatTypeFilter

from sqlalchemy.ext.asyncio import AsyncSession
from handlers.menu_processing import get_menu_content
from keyboards.inline_keyboard import MenuCallBack
from database.orm_qerry import orm_add_user, orm_add_to_cart
from aiogram import Bot


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


async def add_to_cart(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    user = callback.from_user
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


@user_private_router.callback_query(F.data == "order_callback")
async def orderd(callback: types.CallbackQuery):
    await callback.answer(text="Заказ принят в обработку")
    await callback.message.answer()


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


# УДАЛИТЬ ВСЕ ЧТО НИЖЕ
# @user_private_router.message(F.text.lower() == "каталог")
# @user_private_router.message(Command("catalog"))
# async def menu_cmd(message: types.Message, session:AsyncSession):
#     for product in await orm_get_category_products(session): z# добавить category_id
#         await message.answer_photo(
#             product.image,
#             caption=f"<strong>{product.name}\
#             </strong> \n {product.description} \n Стоимость:{round(product.price,2)}руб за мл"
#         )
#     await message.answer("Каталог⬆️")


# @user_private_router.message(F.text.lower() == "о нас")
# @user_private_router.message(Command("about"))
# async def about_cmd(message: types.Message):
#     await message.answer("<i>Выводится информация о боте</i>")


# @user_private_router.message(
#     (F.text.lower() == "Варианты оплаты") | (F.text.contains("оплат"))
# )
# @user_private_router.message(Command("payment"))
# async def payment_cmd(message: types.Message):
#     text = as_marked_section(
#         Bold("Варианты оплаты"),
#         "Картой при получении",
#         "Переводом на карту",
#         marker="✅ ",
#     )

#     await message.answer(text.as_html())


# @user_private_router.message(
#     (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки")
# )
# @user_private_router.message(Command("shiping"))
# async def shiping_cmd(message: types.Message):
#     context = as_marked_section(
#         Bold("Варианты доставки:"), "Курьером 🏎️", "Самовывоз 🦵➡️🍗", marker="✔️"
#     )

#     await message.answer(context.as_html())


# @user_private_router.message(F.text.lower().contains("звон"))
# @user_private_router.message(Command("feedback"))
# async def feedback_cmd(message: types.Message):
#     async with aiofiles.open("feedback_cal.txt", "a", encoding="utf-8") as file:
#         await file.write(
#             f"Перезвонить {message.date}-{message.from_user.id}-{message.from_user.first_name}-{message.from_user.last_name}-{message.from_user.username}\n"
#         )
#         await message.answer("Обратный звонок зарегистрировал")


# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer("номер получен ☎️")
#     await message.answer(str(message.contact))


# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer("Локация получена")
#     await message.answer(str(message.location))


# @user_private_router.message(F.text == "Доп. функции")
# async def secondary_function(message: types.Message):
#     await message.answer("Дополнительные фукции:", reply_markup=secondary_function_kb)


# @user_private_router.message(F.text == "На главную")
# async def return_main_menu(message: types.Message):
#     await message.answer("<strong>Главная:</strong>🏠", reply_markup=start_kb)
