from django.urls import path

from . import views
from . import riot

urlpatterns = [
    path('', views.index, name='index'),
    path('riot.txt', riot.read_file, name='index'),
]