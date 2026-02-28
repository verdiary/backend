import asyncio
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from bot.bot import bot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Synchronize Telegram webhook state with BOT_MODE"

    def handle(self, *args, **options):
        asyncio.run(self._sync())

    async def _sync(self):
        try:
            if settings.BOT_MODE == "polling":
                await bot.delete_webhook(
                    drop_pending_updates=settings.BOT_DROP_PENDING_UPDATES
                )
                self.stdout.write(
                    self.style.SUCCESS("Webhook removed for polling mode")
                )
                logger.info("Webhook removed for polling mode")
                return

            if not settings.BOT_WEBHOOK_URL:
                self.stdout.write(
                    self.style.WARNING(
                        "BOT_WEBHOOK_URL is not set. Skipping webhook registration."
                    )
                )
                logger.warning(
                    "Webhook mode selected but BOT_WEBHOOK_URL is missing."
                )
                return

            await bot.set_webhook(
                url=settings.BOT_WEBHOOK_URL,
                secret_token=settings.BOT_WEBHOOK_TOKEN,
                drop_pending_updates=settings.BOT_DROP_PENDING_UPDATES,
            )
            self.stdout.write(self.style.SUCCESS("Webhook registered"))
            logger.info("Webhook registered at %s", settings.BOT_WEBHOOK_URL)
        finally:
            await bot.session.close()
