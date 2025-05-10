from os import name
from tkinter import N
from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.orm_qerry import (
    orm_add_product,
    orm_get_category_products,
    orm_delete_product,
    orm_get_product,
    orm_update_product,
    orm_get_categories,
    orm_get_info_pages,
    orm_change_banner_image,
)
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply_keyboard import ADMIN_KB, start_kb
from keyboards.inline_keyboard import get_call_back_btns


from sqlalchemy.ext.asyncio import AsyncSession


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


# Код машины состояний
class AddProduct(StatesGroup):
    # Шаги состояний
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        "AddProduct:name": "Введите название заново:",
        "AddProduct:description": "Введите описание заново:",
        "AddProduct:category": "Выберите категорию заново",
        "AddProduct:price": "Введите стоимость заново:",
        "AddProduct:image": "Этот стейт последний, поэтому...",
    }


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def admin_сategory_choice(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btn = {category.name: f"category_{category.id}" for category in categories}

    await message.answer(
        "Выберите категорию", reply_markup=get_call_back_btns(btns=btn)
    )


@admin_router.callback_query(F.data.startswith("category_"))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    for product in await orm_get_category_products(session, int(category_id)):
        await callback.message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_call_back_btns(
                btns={
                    "Удалить": f"delete_{product.id}",
                    "Изменить": f"change_{product.id}",
                },
                sizes=(2,),
            ),
        )
    await callback.answer()
    await callback.message.answer("ОК, вот список товаров ⏫")


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))
    await callback.answer("Товар удален!")
    await callback.message.answer("Товар удален")


@admin_router.message(F.text == "Главная")
async def on_main(message: types.Message):
    await message.answer("Главная", reply_markup=start_kb)


#################################################__FSM__#################################
# изменение уже существующего товара!!!!!!!!!
# name = State()
@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]
    product_for_change = await orm_get_product(session, int(product_id))
    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# name = State()
# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer(
            'Предыдущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}"
            )
            return
        previous = step


# name = State()
# Ловим данные для состояние name и потом меняем состояние на description
@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if len(message.text) >= 100 or len(message.text) < 3:
            await message.answer(
                "Название товара не должно превышать 100 символов. И должно быть не меньше 3 символов\n Введите заново"
            )
            return

        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)


# Хендлер для отлова некорректных вводов для состояния name
@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст названия товара")


# Ловим данные для состояние description и потом меняем состояние на category
@admin_router.message(AddProduct.description, F.text)
async def add_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)
    categories = await orm_get_categories(session)
    btn = {category.name: str(category.id) for category in categories}
    await message.answer(
        "Выберите категорию:", reply_markup=get_call_back_btns(btns=btn)
    )
    await state.set_state(AddProduct.category)


# Хендлер для отлова некорректных вводов для состояния description
@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст описания товара")


# Ловим callback выбора категории
@admin_router.callback_query(AddProduct.category)
async def category_choice(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if int(callback.data) in [
        category.id for category in await orm_get_categories(session)
    ]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Теперь введите цену товара.")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Выберите катеорию из кнопок.")
        await callback.answer()


# Ловим любые некорректные действия, кроме нажатия на кнопку выбора категории
@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите категорию из кнопок.'")


# Ловим данные для состояние price и потом меняем состояние на image
@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return

        await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)


# Хендлер для отлова некорректных ввода для состояния price
@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите стоимость товара")


# Ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == ".":
        await state.update_data(image=AddProduct.product_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(data, session)
        await message.answer("Товар добавлен/изменен", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: {str(e)}\n Обратитесь в службу поддержки", reply_markup=ADMIN_KB
        )
    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото")


############################__FSM__BANNER__###########################################
class AddBanner(StatesGroup):
    image = State()


@admin_router.message(F.text == "Добавить/Изменить баннер")
async def add_banner_image(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        f"Отправте фото баннера. \n В описании к фото укажите для какой страницы ->: \n {",".join(pages_names)}"
    )
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()

    pages_names = [page.name for page in await orm_get_info_pages(session)]

    if for_page not in pages_names:
        await message.answer(
            f"Введите название страницы из списка: \n {'-||-'.join(pages_names)}"
        )
        return
    await orm_change_banner_image(session, for_page, image_id)
    await message.answer("Баннер добавлен/изменен")
    await state.clear()
