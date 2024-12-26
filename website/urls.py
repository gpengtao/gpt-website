"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from marathon.views import hello_world, my_marathon
from see_log.views import query_app_log, app_logs, ivr_logs, see_log_home

urlpatterns = [
    # 首页
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),

    # see_log
    path('see_log/', see_log_home, name='see_log_home'),
    path('see_log/app/', app_logs, name='app_logs'),
    path('see_log/app/<str:app_name>/', query_app_log, name='see_log'),
    path('see_log/ivr/', ivr_logs, name='ivr_logs'),

    # marathon
    path('marathon/', hello_world, name='marathon'),
    path('marathon/my', my_marathon, name='my_marathon'),
]
