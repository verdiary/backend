from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from diary.models import Profile
from django.contrib.auth import get_user_model
from django.utils import timezone

UserModel = get_user_model()


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        try:
            user = await UserModel.objects.aget(telegramuser__id=event.from_user.id)
            profile = (await Profile.objects.aget_or_create(user=user))[0]
            if profile.timezone:
                timezone.activate(profile.timezone)
            else:
                timezone.deactivate()
        except UserModel.DoesNotExist:
            return await handler(event, data)

        data["user"] = user
        data["profile"] = profile

        try:
            return await handler(event, data)
        finally:
            timezone.deactivate()
