# Generated by Django 3.2.9 on 2021-11-30 12:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestAssociate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_id', models.CharField(blank=True, default=False, max_length=10)),
                ('receiver_id', models.CharField(blank=True, default=False, max_length=10)),
                ('cabinet_id', models.CharField(blank=True, default=False, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Associate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cabinet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.cabinet')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]