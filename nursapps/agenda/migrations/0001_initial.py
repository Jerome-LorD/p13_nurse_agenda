# Generated by Django 3.2.9 on 2021-11-27 14:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cabinet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=False, max_length=240, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
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
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sex', models.CharField(blank=True, default=False, max_length=1)),
                ('firstname', models.CharField(blank=True, default=False, max_length=240)),
                ('lastname', models.CharField(blank=True, default=False, max_length=240)),
                ('address', models.CharField(blank=True, default=False, max_length=240)),
                ('phone_number', models.CharField(blank=True, default=False, max_length=10)),
                ('typeofcare', models.CharField(blank=True, default=False, max_length=100)),
                ('numberofcare', models.CharField(blank=True, default=False, max_length=2)),
                ('frequency', models.CharField(blank=True, default=False, max_length=2)),
                ('days', models.CharField(blank=True, default=False, max_length=2)),
                ('cabinet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.cabinet')),
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
