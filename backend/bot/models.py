from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
UserModel = settings.AUTH_USER_MODEL


class TelegramUser(models.Model):
    id = models.BigIntegerField(verbose_name=_("ИД"), primary_key=True)
    user = models.OneToOneField(
        UserModel, verbose_name=_("Пользователь"), on_delete=models.CASCADE
    )
    username = models.CharField(
        max_length=64, verbose_name=_("Имя пользователя"), blank=True, null=True
    )
    first_name = models.CharField(
        max_length=64, verbose_name=_("Имя"), blank=True, null=True
    )
    last_name = models.CharField(
        max_length=64, verbose_name=_("Фамилия"), blank=True, null=True
    )
    language_code = models.CharField(
        max_length=16, verbose_name=_("Язык"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Пользователь Telegram")
        verbose_name_plural = _("Пользователи Telegram")

    def __str__(self):
        if self.username:
            return f"@{self.username}"
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.id}"
