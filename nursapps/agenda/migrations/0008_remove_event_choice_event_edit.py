# Generated by Django 3.2.9 on 2021-12-26 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0007_event_choice_event_edit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='choice_event_edit',
        ),
    ]
