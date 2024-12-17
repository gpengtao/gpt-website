from django.http import HttpResponse
from django.shortcuts import render


def hello_world(request):
    return HttpResponse("hello world，马拉松，你好")


def my_marathon(request):
    races = [
        {
            'year': '2024',
            'date': '2024-09-08',
            'name': '2024新河半程马拉松赛',
            'event': '半马',
            'result': '完赛',
            'net_time': '1:53:01',
            'notes': '首半马'
        },
        {
            'year': '2024',
            'date': '2024-10-20',
            'name': '2024枣庄马拉松',
            'event': '半马',
            'result': '完赛',
            'net_time': '1:46:47',
            'notes': '半马 PB'
        },
        {
            'year': '2024',
            'date': '2024-11-03',
            'name': '2024临沂马拉松',
            'event': '半马',
            'result': '未参加',
            'net_time': '-',
            'notes': '-'
        }
    ]
    return render(request, 'marathon/my_marathon.html', {'races': races})
