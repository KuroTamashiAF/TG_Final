from string import punctuation
from aiogram.filters import Command
from aiogram import F, types, Router
from filters.chat_types import ChatTypeFilter
from aiogram import Bot

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroupe"]))

forbidden_words = {"долбо", "ящер", "лох", "идиот", "сволочь", "гад", "тупица"}


@user_group_router.message(Command("admin"))
async def get_admin_list(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()
        # print(admins_list)


def clean_text(text: str):
    return text.translate(str.maketrans("", "", punctuation))


@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message):
    if forbidden_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(
            f"{message.from_user.first_name} - соблюдайте порядок в чате!!"
        )
        await message.delete()
