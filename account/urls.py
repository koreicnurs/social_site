from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegistrationView.as_view()),
    path('activate/<str:activation_code>/', views.ActivationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('users/search/', views.UsersListViewSet.as_view()),
    # path('follow/<int:pk>/', UserFollowingViewSet.as_view({'post': 'follow'})),
    # path('unfollow/<int:pk>/', UserFollowingViewSet.as_view({'post': 'follow'})),
]
