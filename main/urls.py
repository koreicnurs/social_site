from django.urls import path

from . import views

urlpatterns = [
    path('followers/', views.FollowerList.as_view())
]