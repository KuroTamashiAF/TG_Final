from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Товары 💖": "catalog",
        "Корзина 🛒": "cart",
        "О нас ♦️": "about",
        "Оплата 💸": "payment",
        "Доставка 🚙": "shipping",
    }

    for text, menu_name in btns.items():
        if menu_name == "catalog":
            keyboard.button(
                text=text,
                callback_data=MenuCallBack(level=level + 1, menu_name=menu_name),
            )
        elif menu_name == "cart":
            keyboard.button(
                text=text,
                callback_data=MenuCallBack(level=3, menu_name=menu_name),
            )
        else:
            keyboard.button(
                text=text,
                callback_data=MenuCallBack(level=level, menu_name=menu_name),
            )
    return keyboard.adjust(*sizes).as_markup()


def user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Назад", callback_data=MenuCallBack(level=level - 1, menu_name="main")
    )
    keyboard.button(
        text="Корзина 🛒", callback_data=MenuCallBack(level=3, menu_name="cart")
    )
    for category in categories:
        keyboard.button(
            text=category.name,
            callback_data=MenuCallBack(
                level=level + 1, menu_name=category.name, category=category.id
            ),
        )
    return keyboard.adjust(*sizes).as_markup()


def get_call_back_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()
