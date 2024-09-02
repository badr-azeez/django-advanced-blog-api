from django.urls import path

from . import views

app_name = 'profile'

urlpatterns = [
    path('api/me/update',views.profile_update),
    path('api/posts',views.user_posts),
    path('api/<str:username>',views.profile_retrieve),
]
