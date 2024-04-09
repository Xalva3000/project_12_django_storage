# Generated by Django 5.0.1 on 2024-03-29 20:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0003_rename_planned_date_contract_date_plan_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="specification",
            name="contract",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="specifications",
                to="contracts.contract",
                verbose_name="Контракт",
            ),
        ),
    ]