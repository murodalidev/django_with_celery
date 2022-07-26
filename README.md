# INTEGRATIONS DJANGO WITH CELERY
    mkdir django_with_celery
    cd django_with_celery
    django-admin startproject config .

# Most commands for background tasks
**RUN CELERY WORKER**

    celery -A config.celery worker -l INFO
**RUN CELERY BEAT**

    celery -A config.celery beat -l INFO


# Requirements
    pip install django
    pip install celery
    pip install redis
    pip install django-celery-results (add "django_celery_results" to INSTALLED_APPS)

# Install redis for ubuntu
    sudo apt update
    sudo apt install redis-server
# Testing Redis
    sudo systemctl status redis

# Migrate models
    python manage.py makemigrations
    python manage.py migrate

# `config/settings.py`
    # CELERY settings
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Tashkent'

# `Create new app`
    python manage.py startapp mainapp

# `config/celery.py`
    from __future__ import absolute_import, unicode_literals
    import os
    
    from celery import Celery
    
    # Set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    app = Celery('config')
    app.conf.enable_utc = False
    app.conf.update(timezone='Asia/Tashkent')
    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    # - namespace='CELERY' means all celery-related configuration keys
    #   should have a `CELERY_` prefix.
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # Load task modules from all registered Django apps.
    # Celery beat settings
    app.autodiscover_tasks()
    
    
    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')

# ``config/__init__.py``
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from __future__ import absolute_import, unicode_literals
    from .celery import app as celery_app
    
    __all__ = ('celery_app',)

# ``mainapp/tasks.py``
    from celery import shared_task
    
    
    @shared_task(bind=True)
    def test_task(*args, **kwargs):
        for i in range(10):
            print(i)
        return "test task done"


# ``mainapp/views.py``
    from django.http import HttpResponse
    from .tasks import test_task
    
    
    def test_view(request, *args, **kwargs):
        test_task.delay(*args, **kwargs)
        return HttpResponse("Done")


# ``mainapp/urls.py``
    from django.urls import path
    from .views import test_view
    
    urlpatterns = [
        path('', test_view),
    ]

# SEND MAIL TASK
    python manage.py startapp send_mail_app

# ``config/settings.py``
    # SMTP settings (for sending emails)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'maymail@gmail.com'
    EMAIL_HOST_PASSWORD = '************'
    DEFAULT_FROM_EMAIL = 'Celery <maymail@gmail.com>'


# ``send_mail_app/tasks.py``
    from django.contrib.auth import get_user_model
    from celery import shared_task
    from django.core.mail import send_mail
    from django.conf import settings


    @shared_task(bind=True)
    def send_mail_func(self, *args, **kwargs):
        users = get_user_model().objects.all()
        subject = 'Hi! Celery'
        message = f'Test message'
        for user in users:
            send_mail(subject=subject,
                      message=message,
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[user.email],
                      fail_silently=True
                      )
    
        return "Sent"


# ``send_mail_app/views.py``
    def send_mail_to_all(request, *args, **kwargs):
        username = request.user.username
        send_mail_func.delay()
        return HttpResponse("Sent")

# ``send_mail_app/urls.py``
    from django.urls import path
    from .views import send_mail_to_all
    
    urlpatterns = [
        path('send/', send_mail_to_all),
    ]

# Schedule tasks
    pip install django-celery-beat (add "django_celery_beat" to INSTALLED_APPS; for schedule & periodic tasks)

# Migrate models
    python manage.py makemigrations
    python manage.py migrate


# ``config/settings.py``
    # CELERY BEAT
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


# `config/celery.py`
    from __future__ import absolute_import, unicode_literals
    import os
    
    from celery import Celery
    from celery.schedules import crontab
    
    # Set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    app = Celery('config')
    app.conf.enable_utc = False
    app.conf.update(timezone='Asia/Tashkent')
    
    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    # - namespace='CELERY' means all celery-related configuration keys
    #   should have a `CELERY_` prefix.
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # Celery beat settings
        """Crontab schedule.
    
        A Crontab can be used as the ``run_every`` value of a
        periodic task entry to add :manpage:`crontab(5)`-like scheduling.
    
        Like a :manpage:`cron(5)`-job, you can specify units of time of when
        you'd like the task to execute.  It's a reasonably complete
        implementation of :command:`cron`'s features, so it should provide a fair
        degree of scheduling needs.
    
        You can specify a minute, an hour, a day of the week, a day of the
        month, and/or a month in the year in any of the following formats:
    
        .. attribute:: minute
    
            - A (list of) integers from 0-59 that represent the minutes of
              an hour of when execution should occur; or
            - A string representing a Crontab pattern.  This may get pretty
              advanced, like ``minute='*/15'`` (for every quarter) or
              ``minute='1,13,30-45,50-59/2'``.
    
        .. attribute:: hour
    
            - A (list of) integers from 0-23 that represent the hours of
              a day of when execution should occur; or
            - A string representing a Crontab pattern.  This may get pretty
              advanced, like ``hour='*/3'`` (for every three hours) or
              ``hour='0,8-17/2'`` (at midnight, and every two hours during
              office hours).
    
        .. attribute:: day_of_week
    
            - A (list of) integers from 0-6, where Sunday = 0 and Saturday =
              6, that represent the days of a week that execution should
              occur.
            - A string representing a Crontab pattern.  This may get pretty
              advanced, like ``day_of_week='mon-fri'`` (for weekdays only).
              (Beware that ``day_of_week='*/2'`` does not literally mean
              'every two days', but 'every day that is divisible by two'!)
    
        .. attribute:: day_of_month
    
            - A (list of) integers from 1-31 that represents the days of the
              month that execution should occur.
            - A string representing a Crontab pattern.  This may get pretty
              advanced, such as ``day_of_month='2-30/2'`` (for every even
              numbered day) or ``day_of_month='1-7,15-21'`` (for the first and
              third weeks of the month).
    
        .. attribute:: month_of_year
    
            - A (list of) integers from 1-12 that represents the months of
              the year during which execution can occur.
            - A string representing a Crontab pattern.  This may get pretty
              advanced, such as ``month_of_year='*/3'`` (for the first month
              of every quarter) or ``month_of_year='2-12/2'`` (for every even
              numbered month).
    
        .. attribute:: nowfun
    
            Function returning the current date and time
            (:class:`~datetime.datetime`).
    
        .. attribute:: app
    
            The Celery app instance.
    
        It's important to realize that any day on which execution should
        occur must be represented by entries in all three of the day and
        month attributes.  For example, if ``day_of_week`` is 0 and
        ``day_of_month`` is every seventh day, only months that begin
        on Sunday and are also in the ``month_of_year`` attribute will have
        execution events.  Or, ``day_of_week`` is 1 and ``day_of_month``
        is '1-7,15-21' means every first and third Monday of every month
        present in ``month_of_year``.
        """
    
    app.conf.beat_schedule = {
        'send-email-every-day-at-8': {
            'task': 'send_mail_app.tasks.send_mail_func',
            'schedule': crontab(minute=0, hour=8),
            # 'args': ()
        }
    }

    # Load task modules from all registered Django apps.
    # Celery beat settings
    app.autodiscover_tasks()
    
    
    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')



