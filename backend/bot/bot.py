import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message
from catalogs.models import PlantType, PlantVariety
from diary.models import Plant, SeedStock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F
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
                    "Welcome, {user}! I'm your plant care assistant bot. Use /seeds to view seed stock, /addseeds <type_slug> <quantity> [variety_slug] to add seeds, /plant <id> to plant from stock, /myplants to see your plants, or /today to check today's tasks."
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




@dp.message(Command("seeds"))
async def seeds(message: Message):
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    answer = _("Your seed stock:") + "\n\n"
    found = False

    stocks = (
        SeedStock.objects.filter(
            user__telegramuser__id=message.from_user.id, quantity__gt=0
        )
        .select_related("type", "variety")
        .order_by("type__name", "variety__name")
    )

    async for stock in stocks:
        found = True
        plant_name = stock.type.name
        if stock.variety:
            plant_name += f" {stock.variety.name}"
        answer += f"{stock.id}. 🌱 {plant_name} — {stock.quantity}\n"

    if not found:
        answer = _("Your seed stock is empty.")
    else:
        answer += "\n" + _(
            "Use /addseeds <type_slug> <quantity> [variety_slug] to add seeds."
        )
        answer += "\n" + _("Use /plant <seed_stock_id> to plant one seed.")

    await message.answer(str(answer))




@dp.message(Command("addseeds"))
async def add_seeds(message: Message):
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    parts = (message.text or "").split()
    if len(parts) not in (3, 4) or not parts[2].isdigit():
        await message.answer(
            str(_("Usage: /addseeds <type_slug> <quantity> [variety_slug]"))
        )
        return

    type_slug = parts[1].strip().lower()
    quantity = int(parts[2].strip())
    variety_slug = parts[3].strip().lower() if len(parts) == 4 else None

    if quantity <= 0:
        await message.answer(str(_("Quantity must be greater than 0.")))
        return

    try:
        plant_type = await PlantType.objects.aget(slug=type_slug)
    except PlantType.DoesNotExist:
        await message.answer(str(_("Plant type not found.")))
        return

    variety = None
    if variety_slug:
        try:
            variety = await PlantVariety.objects.aget(
                type=plant_type, slug=variety_slug
            )
        except PlantVariety.DoesNotExist:
            await message.answer(str(_("Plant variety not found for this type.")))
            return

    tg_user = await TelegramUser.objects.select_related("user").aget(
        id=message.from_user.id
    )

    stock_qs = SeedStock.objects.filter(
        user=tg_user.user,
        type=plant_type,
        variety=variety,
    )
    updated = await stock_qs.aupdate(quantity=F("quantity") + quantity)

    if updated == 0:
        await SeedStock.objects.acreate(
            user=tg_user.user,
            type=plant_type,
            variety=variety,
            quantity=quantity,
        )

    stock = await stock_qs.select_related("type", "variety").aget()

    plant_name = stock.type.name
    if stock.variety:
        plant_name += f" {stock.variety.name}"

    await message.answer(
        str(
            _("Added {count} seeds to stock: {plant_name}. Total: {total}.").format(
                count=quantity,
                plant_name=plant_name,
                total=stock.quantity,
            )
        )
    )


@dp.message(Command("plant"))
async def plant_from_seed_stock(message: Message):
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer(str(_("Usage: /plant <seed_stock_id>")))
        return

    stock_id = int(parts[1].strip())

    try:
        stock = await SeedStock.objects.select_related("type", "variety").aget(
            id=stock_id, user__telegramuser__id=message.from_user.id
        )
    except SeedStock.DoesNotExist:
        await message.answer(str(_("Seed stock not found.")))
        return

    if stock.quantity <= 0:
        await message.answer(str(_("This seed stock is empty.")))
        return

    plant = Plant(user=stock.user, type=stock.type, variety=stock.variety)
    await plant.asave()

    stock.quantity -= 1
    await stock.asave(update_fields=["quantity"])

    await message.answer(
        str(
            _("Planted: {plant_name}. Remaining seeds: {quantity}.").format(
                plant_name=plant.name, quantity=stock.quantity
            )
        )
    )


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
