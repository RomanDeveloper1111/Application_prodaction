# Generated by Django 3.2.8 on 2021-10-14 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0023_remove_timesheet_worker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='dataSheet',
            field=models.DateField(default='2021-10-14', verbose_name='Дата'),
        ),
    ]
