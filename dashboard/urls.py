# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('update/', views.update_data, name='update_data'),
    path('download-excel/', views.download_excel, name='download_excel'),
]