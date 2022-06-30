from django.urls import path
from .views import *

app_name = 'salary'
urlpatterns = [
    path('timesheet/', LoadTimeSheet.as_view(), name='load_time_sheet'),
    path('timesheet/<int:department_id>/<str:datetm>/', LoadTimeSheetByTime.as_view(), name='load_time_sheet_by_date'),
    path('view_timesheet/<int:pk>/<int:worker>/<int:day>', ViewTimeSheet.as_view(), name='view_timesheet'),
    path('del_worker_from_timesheet/<int:pk>/<int:worker>', DeleteWorkerFromTimeSheet.as_view(),
         name='del_worker_from_timesheet'),
    path('move-worker/', MoveWorker.as_view(), name="move-worker"),

    path('change-status/<int:pk>', update_status_time_sheet, name='update-status'),
    path('change-status-pay-roll/<int:user_pk>/<str:status>/<str:date>', update_status_pay_roll, name='update-status-pay-roll'),
    path('change-data/', ChangeData.as_view()),

    path('fine/', Fines.as_view(), name='fine'),
    path('add_fine/', AddFine.as_view(), name='add_fine'),
    path('del_fine/<int:pk>', DelFine.as_view(), name='del_fine'),

    path('payroll/<str:request_date>', PayRoll.as_view(), name='payroll'),
    path('test/', AllCategories.as_view(), name='test'),

    path('employees/', ListEmployees.as_view(), name='employees'),
    path('edit_employ/<int:pk>', DetailEmploy.as_view(), name='edit_employ'),

    path('positions/', ListPositions.as_view(), name='positions'),
    path('add-position/', CreatePosition.as_view(), name='add-position'),
    path('edit-position/<int:pk>', EditPosition.as_view(), name='edit-position'),
    path('delete-position/<int:pk>', DeletePosition.as_view(), name='delete-position'),

    path('change-coefficient/', ChangeCoefficient.as_view(), name='change-coefficient'),
    path('change-position/', ChangePosition.as_view(), name='change-position'),

    path('add-worker', AddWorker.as_view(), name='add-worker'),
    path('update-worker/<int:pk>/<str:status>', UpdateWorker.as_view(), name='update-worker'),

    path('departments/', ListDepartments.as_view(), name='departments'),
    path('departments/<int:pk>', UpdateDepartment.as_view(), name='update-depart'),
    path('department-create', CreateDepartment.as_view(), name='create-depart'),
]
