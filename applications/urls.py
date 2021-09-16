from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'applications'
urlpatterns = [
    path('', ChooseApps.as_view(), name='chooseapp'),
    path('apps/', AppList.as_view(), name='apps'),

    path('add/<slug:slug>/', AppCreate.as_view(), name='addApp'),
    path('edit_app/<slug:slug>/<int:pk>/', EditApp.as_view(), name='edit_app'),
    path('delete_app/<int:pk>/', AppDelete.as_view(), name='delete_app'),
    path('update/<int:pk>/', UpdateFromMember.as_view(), name='update_from_members'),
    path('return/<int:pk>/', UpdateForFix.as_view(), name='return_to_manager'),
    path('shipment/<int:pk>/', Shipment.as_view(), name='shipment'),
    path('set_ready/<int:pk>/', SetReady.as_view(), name='set_ready'),
    path('detail_app/<int:pk>/', AppDetail.as_view(), name='detail_app'),
    path('app_done', AppDone.as_view(), name='app_done'),
    path('by_city/<slug>/', AppByFirm.as_view(), name='by_firm'),

    path('content/<int:pk>/', ContentCreate.as_view(), name='content_add'),
    path('delete_content/<int:pk>/', ContentDelete.as_view(), name='delete_content'),
    path('edit_content/<int:pk>/', EditContent.as_view(), name='edit_content'),

    path('otk_update/<slug:slug>/<int:pk>/', UpdateFromOTK.as_view(),  name='otk_update'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

]

