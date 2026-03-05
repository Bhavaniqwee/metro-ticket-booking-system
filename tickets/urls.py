from django.urls import path
from .views import book_ticket_api,cancel_ticket_api,booking_history_api

urlpatterns = [
    path('book/', book_ticket_api),
    path("cancel/<int:ticket_id>/", cancel_ticket_api),
    path("history/", booking_history_api),
]
