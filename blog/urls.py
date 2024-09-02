from django.urls import path
from . import views


urlpatterns = [
    # category
    path('api/categories/',views.categoryies_list),
    
    # posts
    path('api/posts/',views.posts_list_create),
    
    # post
    path('api/post/<slug:slug>',views.post_retrieve),
    path('api/post/<slug:slug>/edit',views.post_update),
    path('api/post/<slug:slug>/delete',views.post_delete),
    path('api/comment/add',views.comment_list_create),
    path('api/comment/<slug:post>',views.comment_retrieve),
    path('api/comment/<int:pk>/update',views.comment_update),
    path('api/comment/<int:pk>/delete',views.comment_delete),
]
