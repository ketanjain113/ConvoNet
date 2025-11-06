from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<str:room>/', views.room, name='room'),
    path('checkview', views.checkview, name='checkview'),
    path('send', views.send, name='send'),
    path('send_media', views.send_media, name='send_media'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
    path('typing/<str:room>/', views.get_typing, name='get_typing'),
    path('typing/set/', views.set_typing, name='set_typing'),
    # DMs
    path('dm/', views.dm_inbox, name='dm_inbox'),
    path('dm/send', views.dm_send, name='dm_send'),
    path('dm/thread/<str:username>/', views.dm_thread, name='dm_thread'),
    path('dm/chat/<str:username>/', views.dm_chat, name='dm_chat'),
    path('dm/unread_count/', views.dm_unread_count, name='dm_unread_count'),
    path('friends/add', views.add_friend, name='add_friend'),
    path('profile/avatar', views.profile_avatar, name='profile_avatar'),
]