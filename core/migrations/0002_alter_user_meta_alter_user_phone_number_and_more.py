# Generated by Django 5.0.6 on 2024-07-01 18:23

import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='meta',
            field=models.JSONField(default={}, verbose_name='MetaData'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(default=None, max_length=128, null=True, region='IN'),
        ),
        migrations.AlterField(
            model_name='user',
            name='standard',
            field=models.CharField(default=None, max_length=10, null=True),
        ),
    ]