# Generated by Django 5.0.6 on 2024-07-04 05:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('batches', '0003_alter_batch_uid_alter_chapter_uid_alter_subject_uid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('uid', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('native', 'Native'), ('youtube', 'YouTube')], max_length=15)),
                ('video_id', models.CharField(max_length=24, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='videos/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=50)),
                ('progress', models.IntegerField(default=0)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lectures', to='batches.chapter')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]