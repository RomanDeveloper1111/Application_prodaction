import numpy as np
from datetime import datetime, date


def busy_days():
    d1 = date(datetime.now().year, datetime.now().month, 1)
    if datetime.now().month == 12:
        d2 = date(datetime.now().year+1, 1, 1)
    else:
        d2 = date(datetime.now().year, datetime.now().month+1, 1)
    return np.busday_count(d1, d2)


def create_calendar(count_days, get_month, get_year):
    days = {}
    for i in range(1, count_days+1):
        days[i] = np.is_busday(date(get_year, get_month, i))
    return days

