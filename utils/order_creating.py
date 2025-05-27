from database.models import Product, User, Cart
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_qerry import orm_get_user_carts
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
        продукт {cart.product.name} \n\
        количество {cart.quantity}  \n\
        стоимость {cart.product.price * cart.quantity}\n"
    return text
