from django.http import HttpResponse
from django.shortcuts import render


def hello_world(request):
    return HttpResponse("hello world，马拉松，你好")


def my_marathon(request):
    races = [
        {
            'date': '2024-09-08',
            'name': '2024新河半程马拉松赛',
            'event': '半马',
            'result': '完赛',
            'net_time': '1:53:01',
            'notes': '首半马'
        },
        {
            'date': '2024-10-20',
            'name': '2024枣庄马拉松',
            'event': '半马',
            'result': '完赛',
            'net_time': '1:46:47',
            'notes': '半马 PB'
        },
        {
            'date': '2024-11-03',
            'name': '2024临沂马拉松',
            'event': '半马',
            'result': '未参加',
            'net_time': '-',
            'notes': '-'
        },
        {
            'date': '2024-12-29',
            'name': 'test1',
            'event': '17公里',
            'result': '还未开始',
            'net_time': '-',
            'notes': '-'
        },
        {
            'date': '2025-01-01',
            'name': 'test2',
            'event': '10公里',
            'result': '还未开始',
            'net_time': '-',
            'notes': '-'
        }
    ]

    # 按日期排序，正序
    races.sort(key=lambda x: x['date'])

    # 按年份分组
    year_group = {}
    for race in races:
        # 从日期中提取年份
        year = race['date'][:4]
        if year not in year_group:
            year_group[year] = []
        year_group[year].append(race)

    return render(request, 'marathon/my_marathon.html', {
        'year_group': year_group,
    })
