# Generated by Django 3.2.9 on 2022-01-07 23:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0003_auto_20220107_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requestassociate',
            old_name='cabinet',
            new_name='cabinet_id',
        ),
        migrations.RenameField(
            model_name='requestassociate',
            old_name='receiver',
            new_name='receiver_id',
        ),
        migrations.RenameField(
            model_name='requestassociate',
            old_name='sender',
            new_name='sender_id',
        ),
    ]
