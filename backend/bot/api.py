import logging
from django.http import HttpResponse
from ninja import NinjaAPI
from pydantic import ValidationError

from aiogram.types import Update

from .bot import dp, bot

logger = logging.getLogger(__name__)

api = NinjaAPI(
    openapi_url=None,
    docs_url=None,
)


@api.post("")
async def index(request):
    try:
        update = Update.model_validate_json(request.body)
        return await dp.feed_update(bot, update)
    except ValidationError as e:
        logger.error("Invalid request", exc_info=True)
        return HttpResponse(e.json(), status=400, content_type="application/json")
