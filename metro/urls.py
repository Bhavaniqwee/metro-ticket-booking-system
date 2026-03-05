from django.urls import path
from .views import calculate_fare_api, stations_api

urlpatterns = [
    path('calculate-fare/', calculate_fare_api, name='calculate_fare'),
    path('stations/', stations_api, name='stations'),
]
