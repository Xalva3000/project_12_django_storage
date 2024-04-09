# Generated by Django 5.0.1 on 2024-04-04 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0006_contract_manager"),
    ]

    operations = [
        migrations.AddField(
            model_name="specification",
            name="variable_weight",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=7, null=True
            ),
        ),
    ]
