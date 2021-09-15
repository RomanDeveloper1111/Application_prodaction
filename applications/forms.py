from .models import *
from django.forms import ModelForm
from django import forms


class AppCreateFormFirst(ModelForm):
    type = forms.ModelChoiceField(queryset=TypeOfApp.objects.filter(pk__in=[1, 2, 3, 4]), label='Тип заявки')
    boss = forms.ModelChoiceField(queryset=Group.objects.filter(name='Коммерция директора').first().user_set.all(),
                                  label='Директор')
    user_accountant = forms.ModelChoiceField(queryset=Group.objects.filter(name='Бухгалтерия').first().user_set.all(),
                                             label='Бухгалтер')
    fabric = forms.ChoiceField(choices=(('-', '---------'), ('50', '50'), ('57', '57')), label='Производство',)

    class Meta:
        model = Application
        fields = ('type', 'name_firm', 'city', 'contact_details', 'user_accountant',
                  'full_cost', 'paid', 'boss', 'fabric')


class AppCreateFormSecond(ModelForm):
    type = forms.ModelChoiceField(queryset=TypeOfApp.objects.filter(pk=5), label='Тип заявки')
    boss = forms.ModelChoiceField(queryset=Group.objects.filter(name='Коммерция директора').first().user_set.all(),
                                  label='Директор')
    user_accountant = forms.ModelChoiceField(queryset=Group.objects.filter(name='Бухгалтерия').first().user_set.all(),
                                             label='Бухгалтер')
    note = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows': '5', 'class': 'note'}), label='Примечание')
    documentation = forms.CharField(widget=forms.widgets.TextInput(attrs={'class': 'note'}), label='Инф. по документам')

    class Meta:
        model = Application
        fields = ('type', 'name_firm', 'city', 'contact_details', 'user_accountant',
                  'boss', 'documentation', 'note')


class CreateContent(ModelForm):
    note = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows': '5', 'class': 'note'}), label='Примечание')
    date = forms.DateTimeField(label='Сроки', widget=forms.widgets.DateTimeInput(attrs={'type': 'date'}))

    class Meta:
        model = Content
        fields = ('name', 'text_number', 'quantity',  'date', 'note',)


class Update(ModelForm):
    note_mistake = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows': '5', 'class': 'note'}), 
                                   label='Замечание')

    class Meta:
        model = Application
        fields = ('note_mistake',)


class UpdateOTK(ModelForm):
    note = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows': '5', 'class': 'note'}), label='Примечание')

    class Meta:
        model = Application
        fields = ('note',)
