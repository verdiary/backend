from datetime import date, timedelta
from typing import Optional

from catalogs.models import Step
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
UserModel = settings.AUTH_USER_MODEL


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
        # Plant.objects.annotate(
        #     sowing_date=PlantEvent.objects.filter(
        #         step__step=Step.SOWING, plant=models.OuterRef("pk")
        #     ).values("date")
        # ).annotate(
        #     harvest_date=models.ExpressionWrapper(
        #         models.F("sowing_date") + models.F("variety__duration_days"),
        #         output_field=models.DateField(),
        #     )
        # ).values()
        sowing = self.events.get(step__step=Step.SOWING)
        if not sowing:
            return None

        return sowing.date + timedelta(days=self.duration_days)

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
            if operation.duration and days > operation.duration:
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
