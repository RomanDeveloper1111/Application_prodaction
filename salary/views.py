import datetime as dt
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, HttpResponse
from django.db.models import Q
from .pylibs.bussy_days import busy_days, create_calendar
from .pylibs.time_sheet import create_dates, delete_worker
import calendar
from .forms import *


class MoveWorker(APIView):
    def post(self, request, format=None):

        department = Department.objects.get(pk=request.data['department'])

        if TimeSheet.objects.filter(department=department.pk, status='open').exists():
            worker = Worker.objects.get(pk=request.data['worker_id'])
            worker.department = department
            worker.save()

            time_sheet = TimeSheet.objects.get(pk=request.data['time_sheet_id'])
            dates_of_timesheet = json.loads(time_sheet.dates)
            worker_in_time_sheet = json.loads(time_sheet.dates)[str(worker.pk)]
            dates_of_timesheet.pop(str(worker.pk))
            time_sheet.dates = json.dumps(dates_of_timesheet)
            time_sheet.save()

            new_timesheet_for_worker = TimeSheet.objects.get(department=department.pk, status='open')
            dates_of_new_timesheet = json.loads(new_timesheet_for_worker.dates)
            dates_of_new_timesheet[worker.pk] = worker_in_time_sheet
            new_timesheet_for_worker.dates = json.dumps(dates_of_new_timesheet)
            new_timesheet_for_worker.save()

        return Response()


def change_position_in_timesheet(time_sheet, worker, position):
    data = json.loads(time_sheet.dates)
    data[str(worker.pk)][0]['position'] = position.pk
    time_sheet.dates = json.dumps(data)
    time_sheet.save()


class ChangePosition(APIView):
    def post(self, request, format=None):
        get_worker = Worker.objects.get(pk=request.data['worker_id'])
        get_position = Position.objects.get(pk=request.data['position_id'])
        get_worker.position = get_position
        get_worker.save()

        get_pre_timesheet = TimeSheet.objects.filter(department=request.data['department'], status='close').last()
        get_current_timesheet = TimeSheet.objects.filter(department=request.data['department'], status='open').last()
        change_position_in_timesheet(get_pre_timesheet, get_worker, get_position)
        change_position_in_timesheet(get_current_timesheet, get_worker, get_position)
        return redirect(f'/payroll/{str(dt.datetime.now().strftime("%Y-%m-%d"))}')


class ChangeCoefficient(APIView):
    def post(self, request, format=None):
        get_coeff = Coefficient.objects.get(pk=request.data['id'])
        get_coeff.count = request.data['value']
        get_coeff.save()
        return Response()


class ListEmployees(LoginRequiredMixin, ListView):
    model = Worker
    template_name = 'salary/employees.html'
    context_object_name = 'workers'


class DetailEmploy(LoginRequiredMixin, UpdateView):
    model = Worker
    template_name = 'salary/edit_employ.html'
    success_url = reverse_lazy('salary:employees')
    form_class = EditEmploy


class ChangeData(APIView):
    def post(self, request, format=None):
        time_sheet = TimeSheet.objects.get(pk=request.data['time_sheet_id'])
        get_dates = json.loads(time_sheet.dates)
        if request.data['name_field'] == 'coefficient':
            get_dates[request.data['worker']][3][0][request.data['name_field']] = request.data['value']
        elif request.data['name_field'] == 'extra_from_foreman':
            get_dates[request.data['worker']][3][1][request.data['name_field']] = request.data['value']
        elif request.data['name_field'] == 'extra_from_director':
            get_dates[request.data['worker']][3][2][request.data['name_field']] = request.data['value']
        elif request.data['name_field'] == 'prepayment':
            get_dates[request.data['worker']][3][3][request.data['name_field']] = request.data['value']
        elif request.data['name_field'] == 'card':
            get_dates[request.data['worker']][3][4][request.data['name_field']] = request.data['value']
        elif request.data['name_field'] == 'breakfast':
            get_dates[request.data['worker']][3][6][request.data['name_field']] = request.data['value']
        elif request.data['name_field'] == 'other':
            get_dates[request.data['worker']][3][7][request.data['name_field']] = request.data['value']
        time_sheet.dates = json.dumps(get_dates)
        time_sheet.save()
        return Response()


def update_status_pay_roll(request, user_pk, status, date):
    get_pay_roll = Payroll.objects.filter(time_sheet__dataSheet__year=dt.datetime.strptime(date, "%Y-%m-%d").year,
                                          time_sheet__dataSheet__month=dt.datetime.strptime(date, "%Y-%m-%d").month,
                                          time_sheet__department__manufacture__director=user_pk)
    for pay_roll in get_pay_roll:
        pay_roll.status = status
        if status == 'avans':
            data_timesheet = json.loads(pay_roll.time_sheet.dates)
            for worker in data_timesheet:
                data_timesheet[str(worker)][3][9]['salary'] = int(Worker.objects.get(pk=worker).position.salary)
            pay_roll.time_sheet.dates = json.dumps(data_timesheet)
            pay_roll.time_sheet.save()
        pay_roll.save()

    return redirect('/salary/payroll/{}'.format(dt.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")))


def update_status_time_sheet(request, pk, status):
    timeSheet = TimeSheet.objects.get(pk=pk)
    pre_status = timeSheet.status
    timeSheet.status = status
    timeSheet.save(update_fields=['status'])
    if status == 'close' and pre_status != 'opened':
        next_month = int(timeSheet.dataSheet.month)+1 if timeSheet.dataSheet.month < 12 else 1
        next_year = int(timeSheet.dataSheet.year) if timeSheet.dataSheet.month < 12 else int(timeSheet.dataSheet.year)+1
        TimeSheet.objects.create(dates=create_dates(Department.objects.get(foreman=request.user.pk).pk, next_month, next_year),
                             dataSheet=timeSheet.dataSheet.replace(month=next_month, year=next_year),
                             foreman=timeSheet.foreman,
                             department=timeSheet.department)
        return redirect('/salary/timesheet/')
    elif pre_status == 'opened':
        return redirect('/')
    else:
        date = dt.datetime.now()
        return redirect('/salary/payroll/{}'.format(date.strftime("%Y-%m-%d")))


class LoadTimeSheetByTime(LoginRequiredMixin, TemplateView):
    template_name = 'salary/load_time_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dat = TimeSheet.objects.filter(
                                       dataSheet__year=dt.datetime.strptime(self.kwargs['datetm'], "%Y-%m-%d").year,
                                       dataSheet__month=dt.datetime.strptime(self.kwargs['datetm'], "%Y-%m-%d").month,
                                       department=Department.objects.get(pk=self.kwargs['department_id'])
                                       ).last()
        try:
            context['errors'] =''
            context['calendar'] = create_calendar(calendar.mdays[dat.dataSheet.month], dat.dataSheet.month,
                                              dat.dataSheet.year)

            context['months'] = ['Январь', 'Февраль', 'Март', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                             'Октябрь', 'Ноябрь', 'Декабрь']

            context['current_time_list'] = dat
            context['positions'] = Position.objects.all()
            depart = Department.objects.get(pk=self.kwargs['department_id'])
            if dat.status == 'open':
                context['workers'] = Worker.objects.filter(department=depart.id).order_by('-position')
            else:
                arr_workers = [x for x in json.loads(dat.dates)]
                context['workers'] = Worker.objects.filter(pk__in=arr_workers)
        except:
            context['errors'] = 'Табеля не существует!'
        context['group'] = Group.objects.get(user=self.request.user.pk)
        context['departments'] = Department.objects.all()
        context['current_department'] = Department.objects.get(pk=self.kwargs['department_id'])
        context['current_date'] = dt.datetime.now().strftime("%Y-%m-%d")

        return context

    def post(self, *args, **kwargs):
        global background
        worker = self.request.POST['worker']
        value = self.request.POST['value']
        day = self.request.POST['day']
        timesheet = TimeSheet.objects.get(pk=self.request.POST['timesheet'])

        dates = json.loads(timesheet.dates)
        count = 0
        if int(day) > 0:
            dates[str(worker)][1][str(day)][0]['count'] = str(value)
        else:
            dates[str(worker)][3][1]['extra_from_foreman'] = value

        for n in dates[str(worker)][1]:
            count += int(dates[str(worker)][1][str(n)][0]['count'])

        dates[str(worker)][2]['sumclocks'] = str(count)
        if self.request.POST['status'] != '':
            dates[str(worker)][1][str(day)][1]['status'] = str(self.request.POST['status'])
            dates[str(worker)][1][str(day)][4]['color'] = '#000'
            if self.request.POST['status'] == 'pass':
                background = '#ffff00b3'
            if self.request.POST['status'] == 'absenteeism':
                background = '#ff0004b3'
            if self.request.POST['status'] == 'sick':
                background = '#00ff10b3'
            if self.request.POST['status'] == 'weekend':
                background = '#1700ffb3'
            if self.request.POST['status'] == 'none':
                background = '#fff'
            if self.request.POST['status'] == 'holiday':
                background = '#505d50'
                dates[str(worker)][1][str(day)][4]['color'] = '#fff'

            if dates[str(worker)][1][str(day)][2]['note'] != '':
                dates[str(worker)][1][str(day)][3]['background'] = \
                    "radial-gradient(circle at 115% -9%, #013f05, #bee2bc 30%, {} 35%)".format(background)
            else:
                dates[str(worker)][1][str(day)][3]['background'] = background
        timesheet.dates = json.dumps(dates)
        if timesheet.status == 'open':
            timesheet.save()
        return redirect('/salary/timesheet/{}/{}'.format(timesheet.department.pk, timesheet.dataSheet.strftime("%Y-%m-%d")))


class LoadTimeSheet(LoginRequiredMixin, TemplateView):
    template_name = 'salary/load_time_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not TimeSheet.objects.filter(department=Department.objects.get(foreman=self.request.user.pk)).exists():
            TimeSheet.objects.create(dates=create_dates(Department.objects.get(foreman=self.request.user.pk).pk, dt.date.today().month, dt.date.today().year),
                                     dataSheet=dt.datetime.now(),
                                     foreman='{} {}'.format(self.request.user.last_name, self.request.user.first_name),
                                     department=Department.objects.get(foreman=self.request.user.pk))

        user_depart = Department.objects.get(foreman=self.request.user.pk)
        if len(TimeSheet.objects.filter(Q(department=user_depart.pk, status='open') | Q(department=user_depart.pk, status='opened'))) == 1:
            dat = TimeSheet.objects.filter(department=Department.objects.get(foreman=self.request.user.pk),
                                       status='open').last()
        else:
            dat = TimeSheet.objects.filter(department=Department.objects.get(foreman=self.request.user.pk),
                                           status='opened').last()


        context['calendar'] = create_calendar(calendar.mdays[dat.dataSheet.month], dat.dataSheet.month, dat.dataSheet.year)
        context['months'] = ['Январь', 'Февраль', 'Март', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                             'Октябрь', 'Ноябрь', 'Декабрь']

        context['current_time_list'] = dat
        context['positions'] = Position.objects.all()
        depart = Department.objects.get(foreman=self.request.user.pk)
        context['departments'] = Department.objects.all()
        context['current_department'] = Department.objects.get(foreman=self.request.user.pk)
        context['errors'] = ''

        if dat.status == 'open' or dat.status == 'opened':
            context['workers'] = Worker.objects.filter(department=depart.id).order_by('-position')
        else:
            arr_workers = [x for x in json.loads(dat.dates)]
            context['workers'] = Worker.objects.filter(pk__in=arr_workers)

        context['group'] = Group.objects.get(user=self.request.user.pk)

        return context

    def post(self, *args, **kwargs):
        global background
        worker = self.request.POST['worker']
        value = self.request.POST['value']
        day = self.request.POST['day']
        position = self.request.POST['position']
        timesheet = TimeSheet.objects.get(pk=self.request.POST['timesheet'])

        dates = json.loads(timesheet.dates)
        dates[str(worker)][0]['position'] = str(position)
        worker_model = Worker.objects.get(pk=worker)
        worker_model.position = Position.objects.get(pk=position)
        worker_model.save()
        count = 0
        if int(day) > 0:
            dates[str(worker)][1][str(day)][0]['count'] = str(value)
        else:
            dates[str(worker)][3][1]['extra_from_foreman'] = value

        for n in dates[str(worker)][1]:
            count += int(dates[str(worker)][1][str(n)][0]['count'])

        dates[str(worker)][2]['sumclocks'] = str(count)
        if self.request.POST['status'] != '':
            dates[str(worker)][1][str(day)][1]['status'] = str(self.request.POST['status'])
            dates[str(worker)][1][str(day)][4]['color'] = '#000'
            if self.request.POST['status'] == 'pass':
                background = '#ffff00b3'
            if self.request.POST['status'] == 'absenteeism':
                background = '#ff0004b3'
            if self.request.POST['status'] == 'sick':
                background = '#00ff10b3'
            if self.request.POST['status'] == 'weekend':
                background = '#1700ffb3'
            if self.request.POST['status'] == 'none':
                background = '#fff'
            if self.request.POST['status'] == 'holiday':
                background = '#505d50'
                dates[str(worker)][1][str(day)][4]['color'] = '#fff'

            if dates[str(worker)][1][str(day)][2]['note'] != '':
                dates[str(worker)][1][str(day)][3]['background'] = \
                    "radial-gradient(circle at 115% -9%, #013f05, #bee2bc 30%, {} 35%)".format(background)
            else:
                dates[str(worker)][1][str(day)][3]['background'] = background
        timesheet.dates = json.dumps(dates)
        timesheet.save()
        return redirect('/salary/timesheet/')


class ViewTimeSheet(LoginRequiredMixin, DetailView):
    model = TimeSheet
    template_name = 'salary/view_timesheet.html'
    context_object_name = 'timesheet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timesheet = TimeSheet.objects.get(pk=self.kwargs['pk'])
        timesheet = json.loads(timesheet.dates)
        context['note'] = timesheet[str(self.kwargs['worker'])][1][str(self.kwargs['day'])][2]['note']
        return context

    def post(self, *args, **kwargs):
        timesheet = TimeSheet.objects.get(pk=self.kwargs['pk'])
        json_dates = json.loads(timesheet.dates)
        json_dates[str(self.kwargs['worker'])][1][str(self.kwargs['day'])][2]['note'] = self.request.POST['note']
        backgr = json_dates[str(self.kwargs['worker'])][1][str(self.kwargs['day'])][3]['background']
        json_dates[str(self.kwargs['worker'])][1][str(self.kwargs['day'])][3]['background'] =\
            "radial-gradient(circle at 115% -9%, #013f05, #bee2bc 30%, {} 35%)".format(backgr)
        timesheet.dates = json.dumps(json_dates)
        timesheet.save()
        return redirect('/salary/timesheet/')


class DeleteWorkerFromTimeSheet(LoginRequiredMixin, DetailView):
    model = TimeSheet
    template_name = 'salary/delete_worker_from_timesheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timesheet'] = TimeSheet.objects.filter(pk__in=delete_worker(self.kwargs['worker']))
        context['worker'] = Worker.objects.get(pk=self.kwargs['worker'])
        return context

    def post(self, *args, **kwargs):
        all_id_sheet_with_worker = delete_worker(self.kwargs['worker'])
        timesheet = TimeSheet.objects.filter(pk__in=all_id_sheet_with_worker)
        for sheet in timesheet:
            json_sheet = json.loads(sheet.dates)
            json_sheet.pop(str(self.kwargs['worker']))
            sheet.dates = json.dumps(json_sheet)
            sheet.save()
        Worker.objects.get(pk=self.kwargs['worker']).delete()
        return redirect('/salary/timesheet/')


class Fines(LoginRequiredMixin, ListView):
    template_name = 'salary/fine.html'
    model = Fine
    context_object_name = 'fines'


class AddFine(LoginRequiredMixin, CreateView):
    model = Fine
    template_name = 'salary/add_fine.html'
    form_class = AddFineForm
    success_url = reverse_lazy('salary:fine')

    def form_valid(self, form):
        form.instance.status = False
        form.instance.dtc = self.request.user.pk
        form.save()
        return redirect("/salary/fine/")


class DelFine(LoginRequiredMixin, DeleteView):
    template_name = 'salary/del_fine.html'
    model = Fine
    context_object_name = 'fine'
    success_url = reverse_lazy('salary:fine')


class PayRoll(LoginRequiredMixin, ListView):
    template_name = 'salary/load_payroll.html'
    context_object_name = 'payrolls'
    model = Payroll

    def get_queryset(self):
        get_all_time_sheets = TimeSheet.objects.filter(dataSheet__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                                       dataSheet__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
                                                       status='close')

        if (not Coefficient.objects.filter(date_create__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                           date_create__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month).exists()):
            Coefficient.objects.create(count=busy_days()*8,
                                       date_create=dt.date(year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                                           month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
                                                           day=1),
                                       status='worker')
            Coefficient.objects.create(count=240,
                                       date_create=dt.date(
                                           year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                           month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
                                           day=1),
                                       status='guard')
        for time_sheet in get_all_time_sheets:
            if (not Payroll.objects.filter(department=time_sheet.department,
                                           time_sheet__dataSheet__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
                                           time_sheet__dataSheet__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                           ).exists()):
                Payroll.objects.create(time_sheet=time_sheet, status=False, department=time_sheet.department,
                                       Note='', name_director=self.request.user)
        if Group.objects.get(user=self.request.user.pk).name == 'Администрация' or Group.objects.get(user=self.request.user.pk).name == 'Бухгалтерия':
            return Payroll.objects.filter(time_sheet__status='close',

                                          time_sheet__dataSheet__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                          time_sheet__dataSheet__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month
                                          )
        else:
            return Payroll.objects.filter(time_sheet__status='close',
                                          time_sheet__department__manufacture__director=self.request.user.pk,
                                          time_sheet__dataSheet__year=dt.datetime.strptime(self.kwargs['request_date'],
                                                                                           "%Y-%m-%d").year,
                                          time_sheet__dataSheet__month=dt.datetime.strptime(self.kwargs['request_date'],
                                                                                            "%Y-%m-%d").month
                                          )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['errors'] = Department.objects.filter(pk__in=[pay_dep.department.pk for pay_dep in Payroll.objects.filter(
                                    time_sheet__dataSheet__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                    time_sheet__dataSheet__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
                                    time_sheet__status='open',
                                    time_sheet__department__manufacture__director=self.request.user.pk)])
        context['group'] = Group.objects.get(user=self.request.user.pk)
        try:
            context['coefficient_worker'] = Coefficient.objects.get(date_create__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                                                        date_create__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
                                                        status='worker')
            context['coefficient_guard'] = Coefficient.objects.get(
                date_create__year=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").year,
                date_create__month=dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d").month,
            status='guard')
        except:
            pass
        context['positions'] = Position.objects.all()
        context['request_date'] = dt.datetime.strptime(self.kwargs['request_date'], "%Y-%m-%d")
        context['current_date'] = dt.datetime.now().strftime("%Y-%m-%d")
        context['user'] = User.objects.get(pk=self.request.user.pk)
        return context


class TestClass(LoginRequiredMixin, TemplateView):
    template_name = 'salary/test.html'


class AllCategories(LoginRequiredMixin, ListView):
    template_name = 'salary/test.html'
    model = Worker


class ListPositions(LoginRequiredMixin, ListView):
    template_name = 'salary/positions.html'
    model = Position
    context_object_name = 'positions'


class CreatePosition(LoginRequiredMixin, CreateView):
    model = Position
    form_class = NewPosition
    template_name = 'salary/add_position.html'
    success_url = reverse_lazy('salary:positions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operation'] = 'Добавление'
        return context


class EditPosition(LoginRequiredMixin, UpdateView):
    template_name = 'salary/add_position.html'
    model = Position
    form_class = NewPosition
    success_url = reverse_lazy('salary:positions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operation'] = 'Редактирование'
        return context


class DeletePosition(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'salary/delete.html'
    success_url = reverse_lazy('salary:positions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['thing'] = 'Должности'
        return context


class AddWorker(LoginRequiredMixin, CreateView):
    model = Worker
    template_name = 'salary/add_worker.html'
    form_class = AddNewWorker
    success_url = reverse_lazy('salary:load_time_sheet')

    def form_valid(self, form):
        form.instance.degree = 3
        form.instance.department = TimeSheet.objects.filter(foreman='{} {}'.format(self.request.user.last_name, self.request.user.first_name)).last().department
        form.save()
        return redirect('/salary/timesheet')


class UpdateWorker(LoginRequiredMixin, UpdateView):
    model = Worker
    template_name = 'salary/add_worker.html'
    form_class = AddNewWorker
    success_url = reverse_lazy('salary:load_time_sheet')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.kwargs['status']
        return context


class ListDepartments(LoginRequiredMixin, ListView):
    model = Department
    context_object_name = 'departments'
    template_name = 'salary/departments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        check_departments = []
        for i in Department.objects.all():
            if i.foreman is None:
                check_departments.append(i.pk)

        context['errors'] = Department.objects.filter(pk__in=check_departments)
        return context


def is_foreman(worker):
    if Department.objects.filter(foreman=worker.pk).exists():
        return True
    else:
        return False


class UpdateDepartment(LoginRequiredMixin, UpdateView):
    model = Department
    form_class = UpdateDepartForm
    template_name = 'salary/update_department.html'
    success_url = reverse_lazy('salary:departments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Редактирование'
        return context

    def form_valid(self, form):
        department = form.instance.name
        manufacture = form.instance.manufacture
        new_foreman = form.instance.foreman
        pre_foreman = Department.objects.get(manufacture=manufacture, name=department).foreman

        if is_foreman(User.objects.get(pk=new_foreman.pk)):

            department_by_new_foreman = Department.objects.get(foreman=User.objects.get(pk=new_foreman.pk).pk)
            department_by_new_foreman.foreman = None
            department_by_new_foreman.save()

        if pre_foreman is not None:
            if TimeSheet.objects.filter(department=Department.objects.get(manufacture=manufacture, name=department),
                                     status='open').exists():
                # Табель прошлого бригадира
                get_timesheet_by_pre_foreman = TimeSheet.objects.get(
                    department=Department.objects.get(manufacture=manufacture, name=department), status='open')
                # Изменение бригадир в табеле
                get_timesheet_by_pre_foreman.foreman = '{} {}'.format(User.objects.get(pk=new_foreman.pk).last_name,
                                                                      User.objects.get(pk=new_foreman.pk).first_name)
                # Сохранение табела
                get_timesheet_by_pre_foreman.save()

                department_by_pre_foreman = Department.objects.get(manufacture=manufacture, name=department)
                department_by_pre_foreman.foreman = User.objects.get(pk=new_foreman.pk)
                department_by_pre_foreman.save()

            if TimeSheet.objects.filter(foreman=User.objects.get(pk=new_foreman.pk).pk, status='open').exists():
                get_timesheet_by_new_foreman = TimeSheet.objects.get(foreman=User.objects.get(pk=new_foreman.pk).pk,
                                                                     status='open')
                get_timesheet_by_new_foreman.foreman = None
                get_timesheet_by_new_foreman.save()
        elif pre_foreman is None:
            check_timsheet_by_department = TimeSheet.objects.filter(
                department=Department.objects.get(manufacture=manufacture, name=department), status='open').exists()
            if check_timsheet_by_department:
                timesheet = TimeSheet.objects.get(
                department=Department.objects.get(manufacture=manufacture, name=department), status='open')
                timesheet.foreman = User.objects.get(pk=new_foreman.pk)
                timesheet.save()

        form.save()

        return redirect("/salary/departments/")


class CreateDepartment(LoginRequiredMixin, CreateView):
    model = Department
    success_url = reverse_lazy('salary:departments')
    template_name = 'salary/update_department.html'
    form_class = CreateDepartForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Добавление'
        return context









