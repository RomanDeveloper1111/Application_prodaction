# Generated by Django 3.2.8 on 2021-10-19 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0031_alter_timesheet_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='dates',
            field=models.JSONField(null=True, verbose_name='Числа'),
        ),
    ]
