import datetime
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import ValidationError


class TypeOfApp(models.Model):
    name = models.CharField(max_length=50, verbose_name='Тип заявки')

    class Meta:
        verbose_name = 'Тип заявки'
        verbose_name_plural = 'Типы заявок'

    def __str__(self):
        return self.name


class Content(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    text_number = models.CharField(max_length=20, verbose_name='Порядковый номер')
    quantity = models.IntegerField(verbose_name='Количество')
    note = models.TextField(max_length=250, verbose_name='Примечание')
    date = models.DateField(null=True, verbose_name='Сроки')
    application = models.ForeignKey('Application', on_delete=models.CASCADE, verbose_name='Заявка', null=True)

    class Meta:
        verbose_name = 'Содержимое заявки'
        verbose_name_plural = 'Содержимое заявок'

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}

        if self.date < datetime.date.today():
            errors['date'] = ValidationError('Дата срока не может быть меньше текущей даты!')

        if self.quantity <= 0:
            errors['quantity'] = ValidationError('Количество должно быть больше 0!')

        if errors:
            raise ValidationError(errors)


class Application(models.Model):
    type = models.ForeignKey(TypeOfApp, on_delete=models.PROTECT, verbose_name='Тип заявки')
    published = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    note_mistake = models.TextField(max_length=1000, verbose_name='Замечание', null=True)
    name_firm = models.CharField(max_length=50, verbose_name='Название фирмы', null=True)
    city = models.CharField(max_length=50, verbose_name='Город', null=True)
    contact_details = models.CharField(max_length=100, verbose_name='Контактные данные', null=True)
    user_accountant = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Бухгалтер',
                                        related_name='accountant', null=True)
    user_manager = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Коммерсант', related_name='manager',
                                     null=True, default=True)
    full_cost = models.DecimalField(max_digits=9, decimal_places=0, default=0, verbose_name='Полная стоимость')
    paid = models.DecimalField(max_digits=9, decimal_places=0, default=0, verbose_name='Оплачено')
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, verbose_name='Статус', null=True)
    note = models.TextField(max_length=1000, verbose_name='Примечание', null=True)
    department = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    boss = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Директор')
    fabric = models.CharField(max_length=10, null=True, verbose_name='Производство')
    documentation = models.CharField(max_length=200, null=True, verbose_name='Информ. по документам')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return "{} | {} | {}".format(self.user_manager, self.city, self.type.name)

    def clean(self):
        errors = {}

        if self.full_cost <= 0:
            errors['full_cost'] = ValidationError('Стоимость должна быть больше 0!')

        if self.paid < 0:
            errors['paid'] = ValidationError('Оплаченная сумма не должна быть менше 0!')

        if errors:
            raise ValidationError(errors)


class Status(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование статуса')

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name
