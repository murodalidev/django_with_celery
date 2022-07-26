from django.http import HttpResponse
from .tasks import test_task


def test_view(request, *args, **kwargs):
    test_task.delay(*args, **kwargs)
    return HttpResponse("Done")


