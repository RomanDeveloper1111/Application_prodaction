import datetime as dt
import json
from .models import *
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.models import Group
from .pylibs.bussy_days import busy_days, create_calendar
from .pylibs.time_sheet import create_dates, delete_worker
import calendar
from .forms import *


class LoadTimeSheet(LoginRequiredMixin, TemplateView):
    template_name = 'salary/load_time_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if (not TimeSheet.objects.filter(foreman='{} {}'.format(self.request.user.last_name,
                                                                self.request.user.first_name),
                                         dataSheet__month=dt.datetime.now().month,
                                         dataSheet__year=dt.datetime.now().year).exists()):
            TimeSheet.objects.create(dates=create_dates(Department.objects.get(foreman=self.request.user.pk).pk),
                                     dataSheet=dt.datetime.now(),
                                     foreman='{} {}'.format(self.request.user.last_name, self.request.user.first_name),
                                     department=Department.objects.get(foreman=self.request.user.pk))

        context['calendar'] = create_calendar(calendar.mdays[dt.date.today().month])
        context['months'] = ['Январь', 'Февраль', 'Март', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                             'Октябрь', 'Ноябрь', 'Декабрь']

        dat = TimeSheet.objects.filter(foreman='{} {}'.format(self.request.user.last_name, self.request.user.first_name)
                                       , dataSheet__month=dt.datetime.now().month,
                                       dataSheet__year=dt.datetime.now().year).first()
        context['current_time_list'] = dat
        depart = Department.objects.get(foreman=self.request.user.pk)
        context['workers'] = Worker.objects.filter(department=depart.id).order_by('-position')

        return context

    def post(self, *args, **kwargs):
        global background
        worker = self.request.POST['worker']
        value = self.request.POST['value']
        day = self.request.POST['day']
        timesheet = TimeSheet.objects.get(pk=self.request.POST['timesheet'])

        dates = json.loads(timesheet.dates)
        count = 0
        dates[str(worker)][1][str(day)][0]['count'] = str(value)

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

            if dates[str(worker)][1][str(day)][2]['note'] is not '':
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
        get_all_time_sheets = TimeSheet.objects.filter(dataSheet__year=dt.datetime.now().year,
                                                       dataSheet__month=dt.datetime.now().month)
        for time_sheet in get_all_time_sheets:
            if (not Payroll.objects.filter(department=time_sheet.department).exists()):
                Payroll.objects.create(time_sheet=time_sheet, status=False, department=time_sheet.department,
                                       Note='', name_director='')

        return Payroll.objects.filter(time_sheet__dataSheet__year=dt.datetime.now().year,
                                      time_sheet__dataSheet__month=dt.datetime.now().month)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['errors'] = Department.objects.exclude(pk__in=[pay_dep.department.pk for pay_dep in Payroll.objects.filter(
                                    time_sheet__dataSheet__year=dt.datetime.now().year,
                                    time_sheet__dataSheet__month=dt.datetime.now().month)])
        return context


class TestClass(LoginRequiredMixin, TemplateView):
    template_name = 'salary/test.html'


class AllCategories(ListView):
    template_name = 'salary/test.html'
    model = Worker



