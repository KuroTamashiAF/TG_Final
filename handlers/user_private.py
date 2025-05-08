from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
import aiofiles
from filters.chat_types import ChatTypeFilter
from keyboards.reply_keyboard import (
    start_kb,
    secondary_function_kb,
)
from aiogram.utils.formatting import Bold, as_marked_section
from database.orm_qerry import orm_get_category_products
from sqlalchemy.ext.asyncio import AsyncSession



user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Здравствуйте это виртуальный помощник. \n " "Я помогу вам сделать заказ =)",
        reply_markup=start_kb,
    )


@user_private_router.message(F.text.lower() == "каталог")
@user_private_router.message(Command("catalog"))
async def menu_cmd(message: types.Message, session:AsyncSession):
    for product in await orm_get_category_products(session): # добавить category_id
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
            </strong> \n {product.description} \n Стоимость:{round(product.price,2)}руб за мл"
        )
    await message.answer("Каталог⬆️")



@user_private_router.message(F.text.lower() == "о нас")
@user_private_router.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer("<i>Выводится информация о боте</i>")


@user_private_router.message(
    (F.text.lower() == "Варианты оплаты") | (F.text.contains("оплат"))
)
@user_private_router.message(Command("payment"))
async def payment_cmd(message: types.Message):
    text = as_marked_section(
        Bold("Варианты оплаты"),
        "Картой при получении",
        "Переводом на карту",
        marker="✅ ",
    )

    await message.answer(text.as_html())


@user_private_router.message(
    (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки")
)
@user_private_router.message(Command("shiping"))
async def shiping_cmd(message: types.Message):
    context = as_marked_section(
        Bold("Варианты доставки:"), "Курьером 🏎️", "Самовывоз 🦵➡️🍗", marker="✔️"
    )

    await message.answer(context.as_html())


@user_private_router.message(F.text.lower().contains("звон"))
@user_private_router.message(Command("feedback"))
async def feedback_cmd(message: types.Message):
    async with aiofiles.open("feedback_cal.txt", "a", encoding="utf-8") as file:
        await file.write(
            f"Перезвонить {message.date}-{message.from_user.id}-{message.from_user.first_name}-{message.from_user.last_name}-{message.from_user.username}\n"
        )
        await message.answer("Обратный звонок зарегистрировал")


@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer("номер получен ☎️")
    await message.answer(str(message.contact))


@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer("Локация получена")
    await message.answer(str(message.location))


@user_private_router.message(F.text == "Доп. функции")
async def secondary_function(message: types.Message):
    await message.answer("Дополнительные фукции:", reply_markup=secondary_function_kb)


@user_private_router.message(F.text == "На главную")
async def return_main_menu(message: types.Message):
    await message.answer("<strong>Главная:</strong>🏠", reply_markup=start_kb)
