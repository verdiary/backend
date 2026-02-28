import logging
from datetime import date, timedelta
from typing import Optional

from catalogs.models import PlantOperation, Step
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField

logger = logging.getLogger(__name__)

# Create your models here.
UserModel = settings.AUTH_USER_MODEL


class Profile(models.Model):
    user = models.OneToOneField(
        UserModel,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="profile",
    )
    timezone = TimeZoneField(
        verbose_name=_("Часовой пояс"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")


class Plant(models.Model):
    user = models.ForeignKey(
        UserModel, verbose_name=_("Пользователь"), on_delete=models.RESTRICT
    )
    name = models.CharField(verbose_name=_("Наименование"), max_length=128, blank=True)

    type = models.ForeignKey(
        "catalogs.PlantType",
        verbose_name=_("Тип"),
        on_delete=models.RESTRICT,
        related_name="plants",
        blank=True,
    )
    variety = models.ForeignKey(
        "catalogs.PlantVariety",
        verbose_name=_("Сорт"),
        on_delete=models.RESTRICT,
        related_name="plants",
        null=True,
        blank=True,
    )

    @property
    def duration_days(self):
        if self.variety:
            return self.variety.duration_days
        return self.type.duration_days

    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"), auto_now_add=True
    )
    updated_at = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    @property
    def planned_harvest_date(self) -> Optional[date]:
        sprouting = self.events.get(step__step=Step.SPROUTING)
        if not sprouting:
            return None

        return sprouting.date + timedelta(days=self.duration_days)

    async def aget_operations_at_date(self, today: date):
        events = [
            s
            async for s in PlantEvent.objects.filter(plant=self)
            .prefetch_related("step")
            .all()
        ]

        operations = [
            o
            async for o in PlantOperation.objects.filter(
                plant_type=self.type_id, since_step__in=[x.step.step for x in events]
            )
            .exclude(until_step__in=[x.step.step for x in events])
            .all()
        ]

        events = {e.step.step: e for e in events}
        for operation in operations:
            related_event = events[operation.since_step]

            start_date = related_event.date  # type: date
            if operation.delay_days:
                start_date += timedelta(days=operation.delay_days)

            if start_date > today:
                continue

            days = (today - start_date).days
            if operation.duration_days and days > operation.duration_days:
                continue

            if days % operation.interval_days == 0:
                yield operation

    def get_operations_at_date(self, today: date):
        operations = self.type.operations.exclude(
            until_step__in=self.events.values_list("step")
        )
        for operation in operations:
            related_event = self.events.filter(step__step=operation.since_step).first()
            if related_event is None:
                continue

            start_date = related_event.date  # type: date
            if operation.delay_days:
                start_date += timedelta(days=operation.delay_days)

            if start_date > today:
                continue

            days = (today - start_date).days
            if operation.duration_days and days > operation.duration_days:
                continue

            if days % operation.interval_days == 0:
                yield operation

    class Meta:
        verbose_name = _("Растение")
        verbose_name_plural = _("Растения")

    def save(self, *args, **kwargs):
        if self.variety:
            self.type = self.variety.type
        if not self.name:
            self.name = self.type.name
            if self.variety:
                self.name += f" {self.variety.name}"
            self.name += f" ({date.today().strftime('%Y-%m-%d')})"
        super().save(*args, **kwargs)

    @staticmethod
    def _parse_period(period: Optional[str], plant_id: Optional[int], period_name: str):
        if not period:
            return None

        romanian_months = {
            "I": 1,
            "II": 2,
            "III": 3,
            "IV": 4,
            "V": 5,
            "VI": 6,
            "VII": 7,
            "VIII": 8,
            "IX": 9,
            "X": 10,
            "XI": 11,
            "XII": 12,
        }

        try:
            start_str, end_str = period.split("-")
            start_day, start_month = start_str.split(".")
            end_day, end_month = end_str.split(".")

            today = date.today()
            start_date = date(today.year, romanian_months[start_month], int(start_day))
            end_date = date(today.year, romanian_months[end_month], int(end_day))

            return start_date, end_date
        except (ValueError, KeyError):
            logger.warning(
                "Failed to parse %s for plant %s", period_name, plant_id
            )
            return None

    @property
    def sowing_period(self):
        if self.variety and self.variety.sowing_period:
            return self.variety.sowing_period
        return self.type.sowing_period

    @cached_property
    def parsed_sowing_period(self):
        return self._parse_period(self.sowing_period, self.id, "sowing period")

    @property
    def planting_period(self):
        if self.variety and self.variety.planting_period:
            return self.variety.planting_period
        return self.type.planting_period

    @cached_property
    def parsed_planting_period(self):
        return self._parse_period(self.planting_period, self.id, "planting period")

    def __str__(self):
        return f"{self.name}"


class PlantEvent(models.Model):
    plant = models.ForeignKey(
        Plant,
        verbose_name=_("Растение"),
        related_name="events",
        on_delete=models.CASCADE,
    )
    step = models.ForeignKey(
        "catalogs.PlantStep",
        verbose_name=_("Этап выращивания"),
        related_name="+",
        on_delete=models.RESTRICT,
    )
    date = models.DateField(_("Дата"), default=date.today, editable=True)
    comment = models.TextField(_("Комментарий"), null=True, blank=True)

    @property
    def name(self):
        return f"{self.step.name}"

    class Meta:
        verbose_name = _("Событие")
        verbose_name_plural = _("События")

        unique_together = ("plant", "step")

    def __str__(self):
        return f"{self.name}"
