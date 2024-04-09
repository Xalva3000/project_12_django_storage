# Generated by Django 5.0.1 on 2024-03-22 14:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0005_alter_product_options_alter_product_cutting_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="time_create",
        ),
        migrations.RemoveField(
            model_name="product",
            name="time_update",
        ),
        migrations.AddField(
            model_name="product",
            name="date_create",
            field=models.DateField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата создания",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="date_update",
            field=models.DateField(auto_now=True, verbose_name="Дата изменения"),
        ),
    ]