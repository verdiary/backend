from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart
from aiogram.types import Message

from .models import TelegramUser


dp = Dispatcher()
bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


@dp.message(CommandStart())
async def start(message: Message):
    if not message.from_user:
        return

    try:
        tg_user = await TelegramUser.objects.aget(id=message.from_user.id)
    except TelegramUser.DoesNotExist:
        user = await get_user_model().objects.acreate(
            username=message.from_user.username or f"tg{message.from_user.id}",
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name or "",
        )
        tg_user = await TelegramUser.objects.acreate(id=message.from_user.id, user=user)

    await message.answer(f"Hello, {tg_user}!")
