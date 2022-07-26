from celery import shared_task


@shared_task(bind=True)
def test_task(*args, **kwargs):
    for i in range(10):
        print(i)
    return "test task done"
