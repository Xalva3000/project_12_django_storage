# Generated by Django 5.0.1 on 2024-04-15 14:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("storage_items", "0003_alter_storageitem_managers_remove_storageitem_owned"),
    ]

    operations = [
        migrations.AddField(
            model_name="storageitem",
            name="weight",
            field=models.DecimalField(decimal_places=2, default=1, max_digits=7),
        ),
    ]
