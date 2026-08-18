from django.urls import path
from . import views

urlpatterns = [
    path('issues/', views.issue_list, name='issue_list'),
    path('reporters/', views.reporter_list, name='reporter_list'),
]