# Generated by Django 5.0.1 on 2024-02-14 00:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_alter_product_weight"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="weight",
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
