# Generated by Django 3.2.9 on 2021-12-30 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0015_alter_event_day_per_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='day_per_week',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
