from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Категория_1', 'Категория_2','Категория_3','Категория_4']

description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": '''AMBRETTE PARFUME мы являмся официальным дистрибьютором 
Парфюмерной компания MG International Fragrance Company на территории России 🇷🇺. 
Отправка по всей России. 
✈🚇🚌🚢🚗 ''',
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Переводом на карту",
        "При получении карта/кеш",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Варианты доставки/заказа:"),
            "Самовынос",
            "СДЭК",
            "Почта",
            marker="✅ ",
        ),
        as_marked_section(Bold("Нельзя:"), "Голуби", marker="❌ "),
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!'
}