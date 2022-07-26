from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def send_mail_func(self, *args, **kwargs):
    users = get_user_model().objects.all()
    subject = 'Hi! Celery'
    message = f'Test message to'
    for user in users:
        send_mail(subject=subject,
                  message=message,
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[user.email],
                  fail_silently=True
                  )

    return "send mail task done"

