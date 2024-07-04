# Generated by Django 5.0.6 on 2024-07-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_user_meta_alter_user_standard'),
    ]

    operations = [
        migrations.AddField(
            model_name='institute',
            name='upload_type',
            field=models.CharField(choices=[('native', 'Native'), ('youtube', 'Youtube')], default='youtube', max_length=10),
        ),
    ]
