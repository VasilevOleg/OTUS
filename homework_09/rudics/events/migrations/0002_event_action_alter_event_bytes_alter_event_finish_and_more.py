# Generated by Django 5.1 on 2024-08-27 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="action",
            field=models.CharField(default="DL", max_length=10),
        ),
        migrations.AlterField(
            model_name="event",
            name="bytes",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="finish",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="start",
            field=models.TimeField(blank=True, null=True),
        ),
    ]
