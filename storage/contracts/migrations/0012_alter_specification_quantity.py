# Generated by Django 5.0.1 on 2024-04-11 23:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0011_rename_payments_payment_alter_contract_manager_share"),
    ]

    operations = [
        migrations.AlterField(
            model_name="specification",
            name="quantity",
            field=models.DecimalField(decimal_places=2, default=1, max_digits=7),
        ),
    ]
