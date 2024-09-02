from django.shortcuts import render
from rest_framework import generics , permissions , filters , exceptions
from .serializers import PostSerializers , CategorySerilaizer , CommentSerializer
from .models import Post , Category , Comment
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.utils import timezone

### My Permissions
class IsOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the object
        return obj.user == request.user

    def handle_no_permission(self):
        raise PermissionDenied("You Don't Have Permission To Edit This Post")
        
################################


## category ##
class CategoriesList(generics.ListAPIView):
    serializer_class = CategorySerilaizer
    queryset = Category.objects.all()

categoryies_list = CategoriesList.as_view()
## end category ##

## posts ##
class PostsListCreate(generics.ListCreateAPIView):
    serializer_class = PostSerializers
    queryset  = Post.objects.all()  
    lookup_field = 'slug'
    authentication_classes = [JWTAuthentication] 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]

    search_fields = ['title','post_excerpt','post_content','publish_at']
    
    filterset_fields = ['title','publish_at']

    ordering_fields = ['title','publish_at']


    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = []
        return super().get_permissions()
    

    def get_queryset(self):
        qs =  super().get_queryset().filter(status='published',publish_at__lte=timezone.now())
        category_name = self.request.GET.get('category',None)
        if category_name:
            qs = qs.filter(category__slug=category_name)
        return qs
    
posts_list_create = PostsListCreate.as_view()

## end posts ##

## post ##
class PostRetrieve(generics.RetrieveAPIView):
    serializer_class = PostSerializers
    queryset  = Post.objects.all()
    lookup_field = 'slug'

    def get_object(self):
        post = super().get_object()
        if post.status == 'published' and post.publish_at <= timezone.now():
            Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
            post.refresh_from_db() # to update the post immediately
            return post

post_retrieve = PostRetrieve.as_view()

class PostUpdate(generics.UpdateAPIView):
    serializer_class = PostSerializers
    queryset = Post.objects.all()
    lookup_field = 'slug'
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerPermission,
    ]
post_update = PostUpdate.as_view()

class PostDelete(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
    lookup_field = 'slug'
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerPermission,
    ]
post_delete = PostDelete.as_view()
## end post ##


## comments ##

class CommentCreate(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

comment_list_create = CommentCreate.as_view()

class CommentRetrieve(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        return super().get_queryset().filter(post__slug=self.kwargs.get('post'))


comment_retrieve = CommentRetrieve.as_view()

class CommentUpdate(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

comment_update = CommentUpdate.as_view()

class CommentDelete(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

    def get_object(self):
        if super().get_object().post.status == 'published':
            return super().get_object()
        else:
            raise exceptions.ValidationError({"detail":"No Comment matches the given query."})
        
comment_delete = CommentDelete.as_view()
## end comments ##
