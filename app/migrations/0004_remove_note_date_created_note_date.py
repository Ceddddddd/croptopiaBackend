# Generated by Django 5.1 on 2024-08-16 12:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_calendar_profit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='date_created',
        ),
        migrations.AddField(
            model_name='note',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
