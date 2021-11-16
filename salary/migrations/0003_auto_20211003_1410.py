# Generated by Django 3.2.7 on 2021-10-03 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0002_remove_payroll_fine'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='card',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Карта'),
        ),
        migrations.AddField(
            model_name='payroll',
            name='other',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Прочее'),
        ),
        migrations.AlterField(
            model_name='fine',
            name='status',
            field=models.BooleanField(verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='breakfast',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Столовая'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='coefficient',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Коэффициент'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='extra_from_director',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Добавочные начальника производства'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='extra_from_foreman',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Добавочные бригадира'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='prepayment',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Аванс'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='salary',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Оклад'),
        ),
        migrations.AlterField(
            model_name='position',
            name='salary',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=2, verbose_name='Оклад'),
        ),
    ]
