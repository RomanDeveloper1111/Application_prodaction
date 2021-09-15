from django.shortcuts import redirect
from .forms import *
from .models import *
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .mixins import ApplicationsMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import Group


# Готов
class AppList(LoginRequiredMixin, ListView):
    permission_required = ('applications.add_application',)
    template_name = 'applications/layout/basic.html'
    model = Application

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contents'] = Content.objects.all()
        context['group'] = Group.objects.get(user=self.request.user.pk)
        context['user'] = self.request.user

        if context['group'].name == 'Администрация':
            pod = Status.objects.all()
        elif context['group'].name == 'ОТК':
            pod = Status.objects.filter(name__in=['Бух готово', 'ОТК частичная готовность'])
        elif context['group'].name == 'Бухгалтерия':
            pod = Status.objects.filter(name__in=['Бух на рассмотрении'])
        elif context['group'].name == 'Кладовщики':
            pod = Status.objects.filter(name__in=['ОТК готово', 'ОТК частичная готовность'])
        elif context['group'].name == 'Коммерция директора':
            pod = Status.objects.filter(name__in=['Коммерция на рассмотрении', 'Коммерция директор', 'Бух отказ',
                                                  'ОТК отказ'])
        elif context['group'].name == 'Менеджеры':
            pod = Status.objects.filter(name__in=['Менеджер', 'Коммерция директор отказ'])
        elif context['group'].name == 'Начальники производства':
            pod = Status.objects.filter(name__in=['ОТК готово', 'Бух готово', 'ОТК частичная готовность'])

        if context['group'].name == 'Менеджеры':
            context['apps'] = Application.objects.filter(status__in=(pod), user_manager=self.request.user)
        elif context['group'].name == 'Коммерция директора':
            context['apps'] = Application.objects.filter(status__in=(pod), boss=self.request.user)
        else:
            context['apps'] = Application.objects.filter(status__in=(pod))
        return context


class AppDone(LoginRequiredMixin, ListView):
    template_name = 'applications/app_done.html'
    model = Application
    context_object_name = 'apps'

    def get_queryset(self):
        return Application.objects.filter(status__in=[8, 9], user_manager=self.request.user).distinct('name_firm')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = Group.objects.get(user=self.request.user.pk)
        return context


class AppByFirm(ListView):
    template_name = 'applications/by_firm.html'
    model = Application
    context_object_name = 'apps'

    def get_queryset(self):
        return Application.objects.filter(name_firm=self.kwargs['slug'], user_manager=self.request.user)


# Не Готов
class AppCreate(PermissionRequiredMixin, ApplicationsMixin, CreateView):
    raise_exception = False
    permission_required = ('applications.add_application',)
    template_name = 'applications/create_app.html'

    def get_success_url(self):
        return reverse("application:content", kwargs={'pk': Application.objects.last().pk})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_operation'] = 'Добавление'
        context['action_name'] = 'Добавить и перейти к оборудованию'
        return context

    def form_valid(self, form):
        user_group = Group.objects.get(user=self.request.user)
        form.instance.user_manager = User.objects.get(pk=self.request.user.pk)
        form.instance.department = Group.objects.get(user=self.request.user)
        if user_group.name == 'Коммерция директора' or user_group.name == 'Администрация':
            if self.kwargs['slug'] == 'first':
                form.instance.status = Status.objects.get(name='Коммерция директор')
            elif self.kwargs['slug'] == 'second':
                form.instance.status = Status.objects.get(name='Отгружено')
        elif user_group.name == 'Менеджеры':
            if self.kwargs['slug'] == 'first':
                form.instance.status = Status.objects.get(name='Менеджер')
            elif self.kwargs['slug'] == 'second':
                form.instance.status = Status.objects.get(name='Отгружено')
        form.save()
        return redirect("/applications/content/{}".format(Application.objects.last().pk))

    def get_form_class(self, *args, **kwargs):
        if self.kwargs['slug'] == 'first':
            return AppCreateFormFirst
        elif self.kwargs['slug'] == 'second':
            return AppCreateFormSecond


# Готов
class EditApp(PermissionRequiredMixin, ApplicationsMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('applications.change_application',)
    model = Application
    template_name = 'applications/create_app.html'
    success_url = reverse_lazy('applications:apps')

    def get_form_class(self):
        if self.kwargs['slug'] == 'first':
            return AppCreateFormFirst
        elif self.kwargs['slug'] == 'second':
            return AppCreateFormSecond

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_operation'] = 'Редактирование'
        context['action_name'] = 'Сохранить'
        return context


class SetReady(PermissionRequiredMixin, ApplicationsMixin, DetailView):
    permission_required = ('applications.change_application', )
    template_name = 'applications/set_ready.html'
    model = Application
    context_object_name = 'app'

    def post(self, request, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        group = Group.objects.get(user=self.request.user.pk)
        if group.name == 'Коммерция директора' or group.name == 'Администрация':
            app.status = Status.objects.get(name='Бух на рассмотрении')
        elif group.name == 'Менеджеры':
            app.status = Status.objects.get(name='Коммерция на рассмотрении')
        app.note_mistake = ''
        app.save()
        return redirect(reverse_lazy('applications:apps'))


class AppDetail(PermissionRequiredMixin, ApplicationsMixin, DetailView):
    model = Application
    permission_required = ('applications.view_application', 'applications.change_application')
    template_name = 'applications/detail_app.html'
    context_object_name = 'app'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cost = Application.objects.get(pk=self.kwargs['pk'])
        context['percent_payment'] = round(cost.paid * 100 / cost.full_cost, 2)
        return context


# Готов
class AppDelete(PermissionRequiredMixin, ApplicationsMixin, DeleteView):
    permission_required = ('applications.delete_application',)
    model = Application
    success_url = reverse_lazy('applications:apps')
    context_object_name = 'app'


# Готов
class ContentCreate(PermissionRequiredMixin, ApplicationsMixin, CreateView):
    permission_required = ('applications.add_content',)
    template_name = 'applications/create_content.html'
    form_class = CreateContent

    def get_success_url(self):
        return reverse('applications:content_add', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_operation'] = 'Добавление'
        context['action_operation'] = 'Добавить'
        context['contents'] = Content.objects.filter(application=self.kwargs['pk'])
        context['apps'] = Application.objects.filter(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.application = Application.objects.get(pk=self.kwargs['pk'])
        form.save()
        return redirect("/applications/content/{}".format(Application.objects.get(pk=self.kwargs['pk']).pk))


# Готов
class EditContent(PermissionRequiredMixin, ApplicationsMixin, UpdateView):
    permission_required = ('applications.change_content',)
    form_class = CreateContent
    model = Content
    template_name = 'applications/create_content.html'
    success_url = reverse_lazy('applications:apps')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_operation'] = 'Редактирование'
        context['action_operation'] = 'Сохранить'
        return context

    def form_valid(self, form):
        form.instance.application = Application.objects.get(pk=Content.objects.get(pk=self.kwargs['pk']).application.pk)
        form.save()
        return redirect("/applications/")


# Готов
class ContentDelete(PermissionRequiredMixin, ApplicationsMixin, DeleteView):
    permission_required = ('applications.delete_content',)
    model = Content
    success_url = reverse_lazy('applications:apps')
    context_object_name = 'content'


# Не Готов
class UpdateFromMember(PermissionRequiredMixin, DetailView):
    permission_required = ('applications.change_application',)
    model = Application
    template_name = 'applications/update_from_member.html'
    success_url = reverse_lazy('applications:apps')

    context_object_name = 'app'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cost = Application.objects.get(pk=self.kwargs['pk'])
        context['percent_payment'] = round(cost.paid * 100 / cost.full_cost, 2)
        return context

    def post(self, request, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        app.status = Status.objects.get(pk=4)
        app.save()
        return redirect('/applications/')


# Не Готов
class UpdateForFix(ApplicationsMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('applications.change_application',)
    model = Application
    template_name = 'applications/return_to_manager.html'
    success_url = reverse_lazy('applications:apps')
    form_class = Update

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Group.objects.get(user=self.request.user.pk).name == 'Бухгалтерия' or \
                Group.objects.get(user=self.request.user.pk).name == 'ОТК':
            context['text'] = 'Возврат в отдел коммерции'
        if Group.objects.get(user=self.request.user.pk).name == 'Коммерция директора' or \
                Group.objects.get(user=self.request.user.pk).name == 'Администрация':
            context['text'] = 'Возврат менеджеру'
        return context

    def form_valid(self, form):
        if Group.objects.get(user=self.request.user.pk).name == 'Бухгалтерия':
            form.instance.status = Status.objects.get(name='Бух отказ')
        elif Group.objects.get(user=self.request.user.pk).name == 'Коммерция директора' or Group.objects.get(
                user=self.request.user.pk).name == 'Администрация':
            form.instance.status = Status.objects.get(name='Коммерция директор отказ')
        elif Group.objects.get(user=self.request.user.pk).name == 'ОТК':
            form.instance.status = Status.objects.get(name='ОТК отказ')
        form.save()
        return redirect('/applications/')


# Готов
class UpdateFromOTK(PermissionRequiredMixin, ApplicationsMixin, UpdateView):
    permission_required = ('applications.change_application',)
    model = Application
    form_class = UpdateOTK
    template_name = 'applications/update_from_otk.html'
    success_url = reverse_lazy('applications:apps')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        if self.kwargs['slug'] == 'full_ready':
            context['status'] = 'полная готовность'
        elif self.kwargs['slug'] == 'part_ready':
            context['status'] = 'частичная готовность'
        return context

    def form_valid(self, form):
        if self.kwargs['slug'] == 'full_ready':
            form.instance.status = Status.objects.get(pk=9)
        elif self.kwargs['slug'] == 'part_ready':
            form.instance.status = Status.objects.get(pk=6)
        form.save()
        return redirect('/applications/')


# Готов
class Shipment(PermissionRequiredMixin, ApplicationsMixin, DetailView):
    model = Application
    permission_required = ('applications.view_application', 'applications.change_application')
    template_name = 'applications/shipment.html'
    context_object_name = 'app'

    def post(self, request, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        app.status = Status.objects.get(name='Отгружено')
        app.save()
        return redirect(reverse_lazy('applications:apps'))

