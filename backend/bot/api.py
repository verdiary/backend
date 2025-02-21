from ninja import NinjaAPI

from aiogram.types import Update

from .bot import dp, bot

api = NinjaAPI(
    openapi_url=None,
    docs_url=None,
)


@api.post("")
async def index(request):
    update = Update.model_validate_json(request.body)
    return await dp.feed_update(bot, update)
