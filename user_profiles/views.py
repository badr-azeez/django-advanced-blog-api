from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework  import generics
from rest_framework.exceptions import NotFound
from .serializers import ProfileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from .models import Profile
from blog.models import Post
from blog.serializers import PostSerializers


## get profile data
class ProfileRetrieve(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        username = self.kwargs.get('username')
        try:
            return Profile.objects.get(user__username=username,user__is_staff=False,user__is_active=True)
        except Profile.DoesNotExist:
            raise NotFound(detail={"result":"Not Found"})

profile_retrieve = ProfileRetrieve.as_view()
################################################################################################


# update profile data 
class ProfileUpdate(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

profile_update = ProfileUpdate.as_view()
################################################################################################


## get auth user posts 
class UserPosts(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter,filters.OrderingFilter]

    search_fields = ['title','post_excerpt','post_content','publish_at']

    ordering_fields = ['title','publish_at']

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)    

user_posts = UserPosts.as_view()
################################################################################################
