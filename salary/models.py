from datetime import datetime
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.serializers.json import DjangoJSONEncoder


class Worker(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    second_name = models.CharField(max_length=50, verbose_name='Фамилия')
    degree = models.IntegerField(default=3, verbose_name='Разряд')
    position = models.ForeignKey('Position', null=True, on_delete=models.SET_NULL, verbose_name='Должность')
    department = models.ForeignKey('Department', null=True, on_delete=models.SET_NULL, verbose_name='Участок')

    def __str__(self):
        return "{} {}".format(self.second_name, self.first_name)

    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = 'Работники'


class Position(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    salary = models.DecimalField(default=0.00, decimal_places=2, max_digits=6, verbose_name='Оклад')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['name']


class Department(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    foreman = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default='null', verbose_name='Бригадир')
    manufacture = models.ForeignKey('Manufacture', on_delete=models.SET_NULL, null=True, default='null',  verbose_name='Производство')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'


class Payroll(models.Model):
    time_sheet = models.ForeignKey('TimeSheet', null=True, on_delete=models.SET_NULL, verbose_name='Табель')
    status = models.CharField(max_length=50, verbose_name='Статус')
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, verbose_name='Участок')
    Note = models.TextField(max_length=500, verbose_name='Примечание')
    name_director = models.CharField(max_length=50, verbose_name='Начальник производства')

    def __str__(self):
        return "{} {}".format(self.status, self.name_director)

    class Meta:
        verbose_name = 'Расчетный лист'
        verbose_name_plural = 'Расчетные листы'


class TimeSheet(models.Model):
    dates = models.JSONField(null=True, verbose_name='Данные')
    dataSheet = models.DateField(default=datetime.now().strftime('%Y-%m-%d'), verbose_name='Дата')
    foreman = models.CharField(max_length=50, verbose_name='Бригадир')
    department = models.ForeignKey(Department, null=True, on_delete=models.CASCADE, verbose_name='Участок')
    status = models.CharField(max_length=50, default='open', null=True)

    def __str__(self):
        return '{} {}'.format(self.foreman, self.dataSheet)

    class Meta:
        verbose_name = 'Табель'
        verbose_name_plural = 'Табеля'


class Fine(models.Model):
    name = models.CharField(max_length=500, verbose_name='Наименование')
    cost = models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Стоимость')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    dtc = models.CharField(max_length=50, verbose_name='ОТК')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Работник')
    status = models.BooleanField(verbose_name='Статус')
    fine_date = models.DateField(auto_now_add=True, verbose_name='Дата штрафа')
    note = models.TextField(max_length=500, verbose_name='Примечание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафы'
        ordering = ['create_date',]


class Coefficient(models.Model):
    count = models.IntegerField(default=168, verbose_name='Сумма часов')
    date_create = models.DateField(verbose_name='Дата коэффициента')
    status = models.CharField(max_length=100, default='null', null=True, verbose_name='Статус')

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = 'Коэффициенты'
        verbose_name_plural ='Коэффициенты'


class Manufacture(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название производства')
    director = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Начальник производства')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производство'
        verbose_name_plural ='Производства'

