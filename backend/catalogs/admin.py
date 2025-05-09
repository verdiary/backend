from django.contrib import admin

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
    fields = ("name", "slug", "description", "planting_period", "duration_days")
    list_display = ("name", "slug", "planting_period", "duration_days")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    inlines = [PlantTypeStepsInline, PlantTypeOperationsInline]


@admin.register(PlantVariety)
class PlantVarietyAdmin(admin.ModelAdmin):
    fields = (
        "type",
        "name",
        "slug",
        "description",
        "planting_period",
        "duration_days",
    )
    list_display = ("full_name", "type", "planting_period", "duration_days")
    list_filter = ("type",)
    ordering = ("type__name", "name")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("type__name", "name")

    def full_name(self, obj):
        return f"{obj.type.name} {obj.name}"
