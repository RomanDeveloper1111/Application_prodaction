# Generated by Django 3.2.7 on 2021-10-05 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0014_alter_timesheet_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='month',
            field=models.DateField(auto_now_add=True, verbose_name='Дата'),
        ),
    ]