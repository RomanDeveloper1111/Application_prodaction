# Generated by Django 4.0.3 on 2022-06-15 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0011_alter_timesheet_datasheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='dataSheet',
            field=models.DateField(default='2022-06-15', verbose_name='Дата'),
        ),
    ]
