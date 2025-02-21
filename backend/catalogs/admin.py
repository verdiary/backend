from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PlantOperation, PlantStep, PlantType, PlantVariety


# Register your models here.
class PlantTypeStepsInline(admin.TabularInline):
    model = PlantStep
    fields = (
        "step",
        "description",
    )
    ordering = ("step",)
    extra = 0


class PlantTypeOperationsInline(admin.TabularInline):
    model = PlantOperation
    fields = (
        "operation",
        "since_step",
        "until_step",
        "delay_days",
        "interval_days",
        "duration_days",
        "description",
    )
    ordering = ("since_step",)
    extra = 0


@admin.register(PlantType)
class PlantTypeAdmin(admin.ModelAdmin):
    fields = ("name", "description", "duration_days", "slug")
    list_display = ("name", "description", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    inlines = [PlantTypeStepsInline, PlantTypeOperationsInline]


@admin.register(PlantVariety)
class PlantVarietyAdmin(admin.ModelAdmin):
    fields = ("type", "name", "description", "duration_days", "slug")
    list_display = ("type", "name")
    list_filter = ("type",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = (
        "type__name",
        "name",
    )
