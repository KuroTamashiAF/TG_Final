from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButtonPollType


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Каталог"),
            KeyboardButton(text="О нас"),
        ],
        [
            KeyboardButton(text="Варианты доставки"),
            KeyboardButton(text="Варианты оплаты"),
        ],
        [
            KeyboardButton(text="Заказать обратный звонок"),
        ],
        [
            KeyboardButton(text="Доп. функции"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вы хотели ?",
)
del_kb = ReplyKeyboardRemove()


start_kb_2 = ReplyKeyboardBuilder()
start_kb_2.add(
    KeyboardButton(text="Каталог"),
    KeyboardButton(text="О нас"),
    KeyboardButton(text="Варианты доставки"),
    KeyboardButton(text="Варианты оплаты"),
    KeyboardButton(text="Заказать обратный звонок"),
)
start_kb_2.adjust(
    2,
    1,
    2,
)


start_kb_3 = ReplyKeyboardBuilder()
start_kb_3.attach(start_kb_2)
start_kb_3.row(KeyboardButton(text="Оставить отзыв"))


secondary_function_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать опрос", request_poll=KeyboardButtonPollType())],
        [KeyboardButton(text="Запрос номера телефона", request_contact=True)],
        [KeyboardButton(text="Запрос локации", request_location=True)],
        [KeyboardButton(text="На главную")],
    ],
    resize_keyboard=True,
)


ADMIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить товар"), KeyboardButton(text="Ассортимент")],
        [KeyboardButton(text="Добавить/Изменить баннер")],
        [KeyboardButton(text="Главная")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
