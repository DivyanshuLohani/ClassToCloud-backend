# Generated by Django 5.0.6 on 2024-07-01 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_user_meta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
