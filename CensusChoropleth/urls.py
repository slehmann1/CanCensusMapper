from django.urls import path

from . import views

urlpatterns = [
    path('', views.test, name='test'),
    path('map/', views.Map.as_view(), name='map_select'),
]