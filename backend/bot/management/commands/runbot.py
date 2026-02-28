import asyncio
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from bot.bot import bot, dp

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run Telegram bot in polling mode"

    def handle(self, *args, **options):
        if settings.BOT_MODE != "polling":
            self.stdout.write(
                self.style.WARNING(
                    "BOT_MODE is not set to polling. Continuing because runbot was called explicitly."
                )
            )

        self.stdout.write(self.style.SUCCESS("Starting Telegram bot in polling mode"))
        asyncio.run(self._run_polling())

    async def _run_polling(self):
        await bot.delete_webhook(
            drop_pending_updates=settings.BOT_DROP_PENDING_UPDATES
        )
        logger.info("Webhook removed before polling startup")

        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()
