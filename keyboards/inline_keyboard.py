from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


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


def products_btns(
    *,
    level: int,
    category: int,
    page: int,
    paginator_btns: dict,
    product_id: int,
    sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Назад 🔙",
        callback_data=MenuCallBack(level=level - 1, menu_name="catalog"),
    )

    keyboard.button(
        text="Корзина 🛒", callback_data=MenuCallBack(level=3, menu_name="cart")
    )
    keyboard.button(
        text="Купить 🤲",
        callback_data=MenuCallBack(
            level=level, menu_name="add_to_cart", product_id=product_id
        ),
    )
    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in paginator_btns.items():
        if menu_name == "next":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page + 1,
                    ).pack(),
                )
            )
        if menu_name == "previous":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page - 1,
                    ).pack(),
                )
            )
    return keyboard.row(*row).as_markup()


def get_btns_in_user_cart_products(
    *,
    level: int,
    page: int | None,
    paginator_btns: dict | None,
    product_id: int | None,
    sizes: tuple[int] = (3,)
):

    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.button(
            text="Удалить",
            callback_data=MenuCallBack(
                level=level, menu_name="delete", product_id=product_id, page=page
            ),
        )

        keyboard.button(
            text="-1",
            callback_data=MenuCallBack(
                level=level, menu_name="decrement", product_id=product_id, page=page
            ),
        )
        keyboard.button(
            text="+1",
            callback_data=MenuCallBack(
                level=level, menu_name="incremrnt", product_id=product_id, page=page
            ),
        )
        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in paginator_btns.items():
            if menu_name == "next":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallBack(
                            level=level,
                            menu_name=menu_name,
                            page=page + 1,
                        ).pack(),
                    )
                )
            if menu_name == "previous":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallBack(
                            level=level,
                            menu_name=menu_name,
                            page=page - 1,
                        ).pack(),
                    )
                )
        keyboard.row(*row)
        row1 = []
        row1.append(
            InlineKeyboardButton(
                text="На главную 🏠",
                callback_data=MenuCallBack(
                    level=0,
                    menu_name="main",
                ).pack(),
            )
        )
        row1.append(
            InlineKeyboardButton(text="Заказать ", callback_data="order_callback"),
        )
        return keyboard.row(*row1).as_markup()
    else:
        keyboard.button(
            text="На главную 🏠", callback_data=MenuCallBack(level=0, menu_name="main")
        )
        return keyboard.adjust(*sizes).as_markup()


def get_call_back_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()
