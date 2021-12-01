# Generated by Django 3.2.9 on 2021-11-30 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cabinet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, default=False, max_length=240, unique=True
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]