import logging
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message
from diary.models import Plant
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from .models import TelegramUser

logger = logging.getLogger(__name__)


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
        try:
            base_username = message.from_user.username or f"tg{message.from_user.id}"
            username = base_username
            suffix = 1
            while True:
                try:
                    user = await get_user_model().objects.acreate(
                        username=username,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name or "",
                    )
                    break
                except IntegrityError:
                    username = f"{base_username}{suffix}"
                    suffix += 1
            tg_user = await TelegramUser.objects.acreate(
                id=message.from_user.id, user=user
            )
        except Exception as e:
            logger.error(e)
            await message.answer(
                "Sorry, an error occurred while creating your account. Please try again later."
            )
            raise

    await message.answer(f"Hello, {tg_user}!")


@dp.message(Command("myplants"))
async def myplants(message: Message):
    answer = "Ваши растения:\n\n"

    async for plants in Plant.objects.filter(
        user__telegramuser__id=message.from_user.id
    ):
        answer += f"{plants.name}\n"
    # plants = await TelegramUser.objects.aget(id=message.from_user.id)

    await message.answer(answer)


@dp.message(Command("today"))
async def today(message: Message):
    answer = "Задачи на сегодня:\n\n"

    async for plant in Plant.objects.filter(
        user__telegramuser__id=message.from_user.id
    ):
        operations = [o async for o in plant.aget_operations_at_date(date.today())]
        if len(operations) == 0:
            continue

        answer += f"<b>{plant}:</b>\n"
        for o in operations:
            answer += f"\t{o}\n"
        answer += "\n\n"

    await message.answer(answer)
