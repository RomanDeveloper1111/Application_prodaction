from django.contrib import admin
from .models import Application, TypeOfApp, Content, Status


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('type', 'published', 'note_mistake', 'name_firm', 'city', 'contact_details', 'user_accountant',
                    'user_manager', 'boss', 'full_cost', 'paid', 'status', 'note', 'department', 'documentation',
                    'fabric')
    list_display_links = ('type', 'published', 'note_mistake', 'name_firm', 'city', 'contact_details',
                          'user_accountant', 'user_manager', 'boss', 'full_cost', 'paid', 'status', 'note',
                          'department', 'documentation', 'fabric')
    search_fields = ('type', 'published', 'note_mistake', 'name_firm', 'city', 'contact_details', 'user_accountant',
                     'user_manager', 'boss', 'full_cost', 'paid', 'status', 'note', 'department')


class TypeOfAppAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'text_number', 'quantity', 'date', 'note', 'application')
    search_fields = ('name', 'text_number', 'quantity', 'date', 'note', 'application')


class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(Application, ApplicationAdmin)
admin.site.register(TypeOfApp, TypeOfAppAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(Status, StatusAdmin)

