import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message
from diary.models import Plant
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .middlewares import UserMiddleware
from .models import TelegramUser

logger = logging.getLogger(__name__)


dp = Dispatcher()
bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
logger.info("Telegram bot initialized")

dp.message.middleware(UserMiddleware())


@dp.message(CommandStart())
async def start(message: Message) -> None:
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    new_account = False
    try:
        tg_user = await TelegramUser.objects.aget(id=message.from_user.id)
        logger.info("Existing user %s started the bot", str(tg_user))
    except TelegramUser.DoesNotExist:
        logger.info("Creating new user for Telegram ID: %s", str(message.from_user.id))
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
                id=message.from_user.id,
                user=user,
                username=username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
            )
            new_account = True
            logger.info("Created new user %s", str(tg_user))
        except Exception as e:
            logger.error("Failed to create user: %s", str(e), exc_info=True)
            await message.answer(
                str(
                    _(
                        "Sorry, an error occurred while creating your account. Please try again later."
                    )
                )
            )
            return

    if new_account:
        await message.answer(
            str(
                _(
                    "Welcome, {user}! I'm your plant care assistant bot. Use /myplants to see your plants or /today to check today's tasks."
                ).format(user=tg_user)
            )
        )
    else:
        await message.answer(str(_("Hello again, {user}!").format(user=tg_user)))


@dp.message(Command("myplants"))
async def myplants(message: Message):
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    answer = _("Your plants:") + "\n\n"

    plants_found = False
    async for plants in Plant.objects.filter(
        user__telegramuser__id=message.from_user.id
    ):
        answer += f"🌱 {plants.name}\n"
        plants_found = True

    if not plants_found:
        answer = _("You don't have any plants yet.")

    await message.answer(str(answer))


@dp.message(Command("today"))
async def today(message: Message):
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    answer = _("Tasks for today:") + "\n\n"

    tasks_found = False
    async for plant in Plant.objects.filter(
        user__telegramuser__id=message.from_user.id
    ):
        operations = [
            o async for o in plant.aget_operations_at_date(timezone.localdate())
        ]
        if len(operations) == 0:
            continue

        tasks_found = True
        answer += f"<b>{plant}:</b>\n"
        for o in operations:
            answer += f" {o}\n"
        answer += "\n\n"

    if not tasks_found:
        answer = _("No tasks scheduled for today! 🌱")

    await message.answer(str(answer))


@dp.message(Command("planting"))
async def planting(message: Message):
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    answer = _("Your future plantings:") + "\n"

    plants_found = False
    now = timezone.localdate()
    plants = (
        Plant.objects.filter(user__telegramuser__id=message.from_user.id)
        .select_related("type", "variety")
        .prefetch_related("events")
        .all()
    )

    for plant in sorted(
        [p async for p in plants],
        key=lambda p: p.parsed_planting_period[0] if p.parsed_planting_period else now,
    ):
        parsed_period = plant.parsed_planting_period
        if parsed_period is None:
            continue

        start_date, end_date = parsed_period
        if end_date < now:
            continue

        plants_found = True
        answer += f"\n🌱 {plant.name}\n"
        answer += f"  {_('Planned planting period')}: {plant.planting_period}\n"

    if not plants_found:
        answer = _("You don't have any plants yet.")

    await message.answer(str(answer))
