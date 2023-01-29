from django.urls import path

from . import views

urlpatterns = [
    path('', views.test, name='test'),
    #path('<str:geoname>/', views.print_characteristics, name='print_characteristics'), 
    path('map/', views.Map.as_view(), name='map')  
]