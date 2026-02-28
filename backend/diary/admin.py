from typing import Any, Iterator

from catalogs.models import PlantStep
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import Plant, PlantEvent, Profile


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "timezone")
    list_filter = ("timezone",)
    search_fields = ("user__username", "user__email")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("user")


class PlantEventInline(admin.TabularInline):
    model = PlantEvent
    fields = ("step", "description", "date", "comment")
    readonly_fields = ("description",)
    ordering = ["date"]
    extra = 0

    def description(self, obj):
        return obj.step.description

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if field is None:
            return field

        if db_field.name == "step" and hasattr(self, "cached_steps"):
            field.choices = self.cached_steps

        return field

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("step")


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type_name",
        "variety_name",
        "sowing_period",
        "planting_period",
        "planned_harvest_date",
        "user",
        "created_at",
        "updated_at",
    )
    list_filter = ("user", "type", "variety", "created_at", "updated_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    inlines = [PlantEventInline]

    @admin.display(ordering="type__name", description=_("Тип"))
    def type_name(self, obj):
        return obj.type

    @admin.display(ordering="variety__name", description=_("Сорт"))
    def variety_name(self, obj):
        return obj.variety

    @admin.display(description=_("Период посадки"))
    def sowing_period(self, obj):
        return obj.sowing_period

    @admin.display(description=_("Период высадки"))
    def planting_period(self, obj):
        return obj.planting_period

    @admin.display(description=_("Дата сбора"))
    def planned_harvest_date(self, obj):
        return obj.planned_harvest_date

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("type", "variety", "user")

    def get_formsets_with_inlines(
        self, request: HttpRequest, obj=None
    ) -> Iterator[Any]:
        for inline in self.get_inline_instances(request, obj):
            if obj is None:
                inline.cached_steps = []
            else:
                inline.cached_steps = [
                    (i.pk, str(i))
                    for i in PlantStep.objects.filter(plant_type=obj.type)
                ]
            yield inline.get_formset(request, obj), inline
