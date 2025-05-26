# from database.models import Product, User, Cart
# from sqlalchemy.ext.asyncio import AsyncSession
# from database.orm_qerry import orm_get_user_carts
# from aiogram import Bot
# from handlers.user_group import CHAT_ID_ORDERS


# async def creating_order(session: AsyncSession, user_id: int, product_id: int, bot:Bot):
#     carts = await orm_get_user_carts(session, user_id)

#     for cart in carts:
#         bot.send_message(chat_id=CHAT_ID_ORDERS, text="hello")
#     return 
     
