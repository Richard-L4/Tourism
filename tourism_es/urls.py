from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('event-details/', views.event_details, name='event-details'),
    path('edit-comment/', views.edit_comment, name='edit-comment'),
    path('delete-comments/', views.delete_comments, name='delete-comments'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('confirm-logout/', views.confirm_logout, name='confirm-logout'),
    path('register/', views.register, name='register')
]
