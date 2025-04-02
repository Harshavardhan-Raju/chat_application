
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    # path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('userprofile/', views.userprofile_view, name='userprofile'),
    path('logout/', views.logout_view, name='logout'),
    # New chat URLs
    path('chat/', views.chat_view, name='chat'),
    path('chat/<str:username>/', views.specific_chat, name='specific_chat'),
    path('search/', views.search_users, name='search_users'),
]