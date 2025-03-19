import logging
from typing import Optional

from aiogram.types import Update
from aiogram.dispatcher.event.bases import UNHANDLED, REJECTED
from django.conf import settings
from django.http import HttpResponse
from ninja import Header, NinjaAPI
from pydantic import ValidationError

from .bot import bot, dp

logger = logging.getLogger(__name__)

api = NinjaAPI(
    openapi_url=None,
    docs_url=None,
)


@api.post("")
async def index(
    request,
    secret_token: Optional[str] = Header(
        alias="X-Telegram-Bot-Api-Secret-Token", default=None
    ),
):
    if settings.BOT_WEBHOOK_TOKEN and secret_token != settings.BOT_WEBHOOK_TOKEN:
        return HttpResponse("", status=401)

    try:
        update = Update.model_validate_json(request.body)
        response = await dp.feed_update(bot, update)
        if response is UNHANDLED:
            logger.warning("Unhandled update: %s", update)
            return HttpResponse("", status=200)

        if response is REJECTED:
            logger.warning("Rejected update: %s", update)
            return HttpResponse("", status=200)

        return response
    except ValidationError as e:
        logger.error("Invalid request", exc_info=True)
        return HttpResponse(e.json(), status=400, content_type="application/json")
