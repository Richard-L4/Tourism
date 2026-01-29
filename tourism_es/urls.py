from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('event-details/<int:pk>/', views.event_details, name='event-details'),
    path('edit-comment/<int:pk>/', views.edit_comment, name='edit-comment'),
    path('delete-comments/<int:pk>/',
         views.delete_comments, name='delete-comments'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('confirm-logout/', views.confirm_logout, name='confirm-logout'),
    path('register/', views.register, name='register'),
    path('toggle-reaction/<int:comment_id>/<str:reaction_type>/',
         views.toggle_reaction, name='toggle_reaction'),
    path('card/<int:pk>/rate/', views.rate_card, name='rate_card'),

]
