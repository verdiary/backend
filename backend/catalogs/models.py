from django.db import models
from django.utils.translation import gettext_lazy as _


class Step(models.TextChoices):
    SEED_PREPARATION = "10-seed_preparation", _("Подготовка семян")
    SOWING = "20-sowing", _("Посев")
    SPROUTING = "30-sprouting", _("Всходы")
    TRANSPLANTING = "40-transplanting", _("Пересадка")
    PLANTING_PREPARATION = "50-planting_preparation", _("Подготовка к высадке")
    PLANTING = "60-planting", _("Высадка")
    BLOOMING = "65-blooming", _("Цветение")
    PINCHING_OUT = "70-pinching_out", _("Пасынкование")
    TIE_UP = "80-tie_up", _("Подвязка")
    HARVESTING = "90-harvesting", _("Сбор урожая")


class Operation(models.TextChoices):
    WATERING = "watering", _("Полив")
    FERTILIZING = "fertilizing", _("Подкормка")
    HARDENING = "hardening", _("Закаливание")
    HILLING = "hilling", _("Окучивание")


# Create your models here.
class PlantType(models.Model):
    id = models.AutoField(verbose_name=_("ИД"), primary_key=True)
    slug = models.SlugField(verbose_name=_("Код"), unique=True)
    name = models.CharField(verbose_name=_("Наименование"), max_length=128)
    description = models.TextField(verbose_name=_("Описание"))

    duration_days = models.IntegerField(verbose_name=_("Срок созревания (дн.)"))

    class Meta:
        verbose_name = _("Тип")
        verbose_name_plural = _("Типы")

        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class PlantVariety(models.Model):
    id = models.AutoField(verbose_name=_("ИД"), primary_key=True)
    type = models.ForeignKey(
        PlantType,
        verbose_name=_("Тип"),
        on_delete=models.RESTRICT,
        related_name="varieties",
    )
    slug = models.SlugField(verbose_name=_("Код"))
    name = models.CharField(verbose_name=_("Наименование"), max_length=128)
    description = models.TextField(verbose_name=_("Описание"))

    duration_days = models.IntegerField(verbose_name=_("Срок созревания (дн.)"))

    class Meta:
        verbose_name = _("Сорт")
        verbose_name_plural = _("Сорта")

        unique_together = ("type", "slug")

        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class PlantStep(models.Model):
    id = models.AutoField(verbose_name=_("ИД"), primary_key=True)
    description = models.TextField(verbose_name=_("Описание"))
    plant_type = models.ForeignKey(
        PlantType,
        verbose_name=_("Тип"),
        related_name="steps",
        on_delete=models.CASCADE,
    )
    step = models.CharField(
        verbose_name=_("Этап"),
        max_length=32,
        choices=Step,
    )

    @property
    def name(self):
        return Step(self.step).label

    class Meta:
        verbose_name = _("Этап выращивания")
        verbose_name_plural = _("Этапы выращивания")
        ordering = ["plant_type", "step"]

        unique_together = ("plant_type", "step")

    def __str__(self):
        return f"{self.name}"


class PlantOperation(models.Model):
    id = models.AutoField(verbose_name=_("ИД"), primary_key=True)
    description = models.TextField(verbose_name=_("Описание"))
    operation = models.CharField(
        verbose_name=_("Операция"),
        max_length=32,
        choices=Operation,
    )
    plant_type = models.ForeignKey(
        PlantType,
        verbose_name=_("Тип"),
        related_name="operations",
        on_delete=models.RESTRICT,
    )

    since_step = models.CharField(
        verbose_name=_("С этапа"),
        max_length=32,
        choices=Step,
    )
    until_step = models.CharField(
        verbose_name=_("По этап"),
        max_length=32,
        choices=Step,
    )

    delay_days = models.IntegerField(
        verbose_name=_("Ожидание (дн.)"), null=True, blank=True
    )
    interval_days = models.IntegerField(verbose_name=_("Периодичность (дн.)"))
    duration_days = models.IntegerField(
        verbose_name=_("Продолжительность (дн.)"), null=True, blank=True
    )

    @property
    def name(self):
        return Operation(self.operation).label

    class Meta:
        verbose_name = _("Операция")
        verbose_name_plural = _("Операции")

    def __str__(self):
        return f"{self.name}"
