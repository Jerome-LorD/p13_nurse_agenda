# Generated by Django 3.2.9 on 2021-12-21 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0003_rename_days_number_event_nb_visit_per_days'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='nb_visit_per_days',
            new_name='days_number',
        ),
    ]