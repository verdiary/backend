# Generated by Django 5.1.6 on 2025-02-21 23:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TelegramUser",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        primary_key=True, serialize=False, verbose_name="ИД"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        null=True,
                        verbose_name="Имя пользователя",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=64, null=True, verbose_name="Имя"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=64, null=True, verbose_name="Фамилия"
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        blank=True, max_length=16, null=True, verbose_name="Язык"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь Telegram",
                "verbose_name_plural": "Пользователи Telegram",
            },
        ),
    ]
