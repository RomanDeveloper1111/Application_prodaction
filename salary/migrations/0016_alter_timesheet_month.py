# Generated by Django 3.2.7 on 2021-10-05 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0015_alter_timesheet_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='month',
            field=models.DateField(default='2021-10-05', verbose_name='Дата'),
        ),
    ]