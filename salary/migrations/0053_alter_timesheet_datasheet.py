# Generated by Django 3.2.8 on 2021-11-05 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0052_alter_timesheet_datasheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='dataSheet',
            field=models.DateField(default='2021-11-05', verbose_name='Дата'),
        ),
    ]
