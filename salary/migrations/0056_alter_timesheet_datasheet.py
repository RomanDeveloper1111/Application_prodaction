# Generated by Django 3.2.8 on 2021-11-10 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0055_alter_timesheet_datasheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='dataSheet',
            field=models.DateField(default='2021-11-10', verbose_name='Дата'),
        ),
    ]
