# Generated by Django 3.2.8 on 2021-10-14 10:29

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0024_alter_timesheet_datasheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='dates',
            field=models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, null=True, verbose_name='Числа'),
        ),
    ]
