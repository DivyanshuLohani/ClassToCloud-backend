# Generated by Django 5.0.6 on 2024-07-01 18:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_alter_verifycode_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifycode',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 19, 38, 27, 14025, tzinfo=datetime.timezone.utc)),
        ),
    ]