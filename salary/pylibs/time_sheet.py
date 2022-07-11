from ..models import *
from json import dumps
import calendar
import datetime as dt
from .bussy_days import create_calendar, busy_days
import json


def create_dates(depart, get_month, get_year):
    cln = {}
    workers = Worker.objects.filter(department=depart).order_by('-position')
    calen = create_calendar(calendar.mdays[get_month], get_month, get_year)

    for worker in workers:
        if worker.position.name in ['Охранник', ]:
            norm_clocks = int(len(calen.keys()))/3*24
        else:
            norm_clocks = int(busy_days())*8
        cln[worker.pk] = [{'position': worker.position.pk}, {}, {}, [{'coefficient': 1.0}, {'extra_from_foreman': 0.00},
                                                                 {'extra_from_director': 0.00}, {'prepayment': 0.00},
                                                                 {'card': 0.00}, {}, {'breakfast': 0.00},
                                                                 {'other': 0.00}, {'norm_clocks': norm_clocks},
                                                                 {'salary': 0.00},

                                                                 ]]
        summ = 0
        for key, value in calen.items():
            if not value:
                count = 0
                background = '#505d50'
                color = '#fff'
            else:
                count = 0
                background = '#fff'
                color = '#000'
            cln[worker.pk][1][key] = [{'count': count}, {'status': 'null'},
                                      {'note': ''}, {'background': background},
                                      {'color': color}]
            summ += count
        cln[worker.pk][2] = {'sumclocks': summ}
    return dumps(cln)


def add_worker(dictionary, worker):
    dates = json.loads(dictionary.dates)
    calen = create_calendar(calendar.mdays[dictionary.dataSheet.month], dictionary.dataSheet.month, dictionary.dataSheet.year)
    if worker.position.name in ['Охранник', ]:
        norm_clocks = int(len(calen.keys())) / 3 * 24
    else:
        norm_clocks = int(busy_days()) * 8

    dates[str(worker.pk)] = [{'position': worker.position.pk}, {}, {}, [{'coefficient': 1.0}, {'extra_from_foreman': 0.00},
                                                                    {'extra_from_director': 0.00}, {'prepayment': 0.00},
                                                                    {'card': 0.00}, {}, {'breakfast': 0.00},
                                                                    {'other': 0.00}, {'norm_clocks': norm_clocks},
                                                                    {'salary': 0.00},
                                                                    ]]

    summ = 0
    for key, value in calen.items():
        if not value:
            count = 0
            background = '#505d50'
            color = '#fff'
        else:
            count = 0
            background = '#fff'
            color = '#000'
        dates[str(worker.pk)][1][key] = [{'count': count}, {'status': 'null'},
                                         {'note': ''}, {'background': background},
                                         {'color': color}]
        summ += count


    dates[str(worker.pk)][2] = {'sumclocks': summ}
    timesheet = TimeSheet.objects.get(pk=dictionary.pk)
    timesheet.dates = json.dumps(dates)
    timesheet.save()


def delete_worker(worker):
    get_all_sheets = TimeSheet.objects.all()
    all_id_sheet_with_worker = []
    for sheet in get_all_sheets:
        json_sheet = json.loads(sheet.dates)
        if json_sheet.get(str(worker)) is not None:
            all_id_sheet_with_worker.append(sheet.pk)
    return all_id_sheet_with_worker
