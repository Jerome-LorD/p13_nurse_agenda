# Generated by Django 3.2.9 on 2021-12-26 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0006_remove_event_choice_event_edit'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='choice_event_edit',
            field=models.CharField(max_length=100, null=True),
        ),
    ]