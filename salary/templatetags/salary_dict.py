from django import template
import json
from django.db.models import Sum, Q
from ..pylibs.time_sheet import add_worker
from ..models import *
import datetime as dt

register = template.Library()


@register.simple_tag(name='dict')
def search_dict(dictionary, worker, numb, method):
    dates = json.loads(TimeSheet.objects.get(pk=dictionary.pk).dates)
    if method == 'count':
        return dates['{}'.format(worker)][1]['{}'.format(numb)][0]['count']
    if method == 'background':
        return dates['{}'.format(worker)][1]['{}'.format(numb)][3]['background']
    if method == 'color':
        return dates['{}'.format(worker)][1]['{}'.format(numb)][4]['color']


@register.filter(name='counttime')
def counttime(dictionary, worker):
    dates = json.loads(dictionary.dates)
    if dates.get(str(worker.pk)) is None:
        add_worker(dictionary, worker)
    dates = json.loads(TimeSheet.objects.get(pk=dictionary.pk).dates)
    return dates[str(worker.pk)][2]['sumclocks']


@register.filter(name='convert')
def convert(payroll):
    return json.loads(payroll.time_sheet.dates)


@register.simple_tag(name='get_method')
def payroll(dictionary, worker, method):
    if method == 'position':
        return Position.objects.get(pk=dictionary[worker][0][method])
    if method == 'worker':
        return Worker.objects.get(pk=worker)
    if method == 'worker':
        return Worker.objects.get(pk=worker)
    if method == 'salary':
        return Worker.objects.get(pk=worker).position.salary
    if method == 'degree':
        return Worker.objects.get(pk=worker).degree
    if method == 'coefficient':
        return dictionary[worker][3][0][method]
    if method == 'sumclocks':
        return dictionary[worker][2][method]
    if method == 'extra_from_foreman':
        return dictionary[worker][3][1][method]
    if method == 'extra_from_director':
        return dictionary[worker][3][2][method]
    if method == 'prepayment':
        return dictionary[worker][3][3][method]
    if method == 'card':
        return dictionary[worker][3][4][method]
    if method == 'breakfast':
        return dictionary[worker][3][6][method]
    if method == 'other':
        return dictionary[worker][3][7][method]
    if method == 'fines':
        summa = Fine.objects.aggregate(sum=Sum('cost', filter=Q(worker=worker,
                                                                create_date__year=dt.datetime.now().year,
                                                                create_date__month=dt.datetime.now().month,
                                                                )))
        if summa['sum'] == None: summa['sum'] = 0.00
        return summa['sum']
    if method == 'norm_clocks':
        return dictionary[worker][3][8][method]






