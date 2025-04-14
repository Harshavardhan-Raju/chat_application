# yourapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('userprofile/', views.userprofile_view, name='userprofile'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/<str:username>/', views.specific_chat, name='specific_chat'),
    path('search/', views.search_users, name='search_users'),
    path('chat/<str:username>/check_messages/', views.check_new_messages, name='check_new_messages'),
    
    # Group chat URLs
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_chat, name='group_chat'),
    path('groups/<int:group_id>/manage/', views.manage_group, name='manage_group'),
    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),

        # In urls.py
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
]