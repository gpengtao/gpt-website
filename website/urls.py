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

from marathon.views import hello_world
from marathon.views import my_marathon
from see_log.views import query_app_log, recent_log_stat

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),

    # see_log
    path('see_log/<str:app_name>/', query_app_log, name='see_log'),
    path('see_log/', recent_log_stat, name='recent_log_stat'),

    # marathon
    path('marathon/', hello_world, name='marathon'),
    path('marathon/my', my_marathon, name='my_marathon'),
]
