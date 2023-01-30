from django.urls import path

from . import views

urlpatterns = [
    path('', views.Map.as_view(), name='map_select'),
]