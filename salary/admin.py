from django.contrib import admin
from .models import Worker, Fine, Payroll, TimeSheet, Position, Department, Manufacture, Coefficient


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'second_name', 'degree', 'position', 'department')
    list_display_links = ('first_name', 'second_name', 'degree', 'position', 'department')


class FineAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'create_date', 'dtc', 'worker', 'status', 'fine_date', 'note')
    list_display_links = ('name', 'cost', 'create_date', 'dtc', 'worker', 'status', 'fine_date', 'note')


class PayrollAdmin(admin.ModelAdmin):
    list_display = ('time_sheet', 'department', 'status', 'Note', 'name_director')
    list_display_links = ('time_sheet', 'department', 'status', 'Note', 'name_director')


class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('pk', 'dataSheet', 'foreman', 'department', 'status')
    list_display_links = ('dataSheet', 'foreman', 'department', 'status')


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary')
    list_display_links = ('name', 'salary')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'foreman', 'manufacture')
    list_display_links = ('name', 'foreman', 'manufacture')


class CoefficientAdmin(admin.ModelAdmin):
    list_display = ('count', 'date_create')
    list_display_links = ('count', 'date_create')


class ManufactureAdmin(admin.ModelAdmin):
    list_display = ('name', 'director')


admin.site.register(Worker, WorkerAdmin)
admin.site.register(Fine, FineAdmin)
admin.site.register(Payroll, PayrollAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Coefficient, CoefficientAdmin)
admin.site.register(Manufacture, ManufactureAdmin)

