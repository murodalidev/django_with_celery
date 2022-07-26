from django.urls import path
from .views import send_mail_to_all

urlpatterns = [
    path('send/', send_mail_to_all),
]