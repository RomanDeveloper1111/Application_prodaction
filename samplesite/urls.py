
from django.contrib import admin
from django.urls import path, include

app_name = 'samplesite'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('applications.urls')),
    path('salary/', include('salary.urls')),
]
