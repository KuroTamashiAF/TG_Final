from database.models import Product, User, Cart
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_qerry import orm_get_user_carts, orm_delete_all_carts_user
from aiogram.types import CallbackQuery


async def creating_order(
    *,
    session: AsyncSession,
    user_id: int,
    callback: CallbackQuery,
):
    carts = await orm_get_user_carts(session, user_id)
    text = ""
    for cart in carts:
        text += f"Примите заказ пользователь: {callback.from_user.username} \n\
    Продукт {cart.product.name} \n\
    Количество {cart.quantity}  \n\
    Стоимость {round(cart.product.price * cart.quantity),2} руб\n"

    await orm_delete_all_carts_user(session=session, user_id=user_id)
    return text
