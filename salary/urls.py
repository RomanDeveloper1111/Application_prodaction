from django.urls import path
from .views import *

app_name = 'salary'
urlpatterns = [
    path('timesheet/', LoadTimeSheet.as_view(), name='load_time_sheet'),
    path('view_timesheet/<int:pk>/<int:worker>/<int:day>', ViewTimeSheet.as_view(), name='view_timesheet'),
    path('del_worker_from_timesheet/<int:pk>/<int:worker>', DeleteWorkerFromTimeSheet.as_view(),
         name='del_worker_from_timesheet'),

    path('fine/', Fines.as_view(), name='fine'),
    path('add_fine/', AddFine.as_view(), name='add_fine'),
    path('del_fine/<int:pk>', DelFine.as_view(), name='del_fine'),

    path('payroll/', PayRoll.as_view(), name='payroll'),
    path('test/', AllCategories.as_view(), name='test'),
]
