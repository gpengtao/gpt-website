from django.http import HttpResponse

def hello_world(request):
    return HttpResponse("hello world，马拉松，你好")
