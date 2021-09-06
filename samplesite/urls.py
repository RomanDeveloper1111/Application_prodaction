
from django.contrib import admin
from django.urls import path, include

app_name = 'samplesite'
urlpatterns = [
    path('bboard/', include('bboard.urls')),
    path('admin/', admin.site.urls),
    path('applications/', include('applications.urls')),
]
