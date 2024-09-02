from rest_framework import serializers
from .models import Post, Category, Comment
from django.contrib.auth.models import User

import re,bleach


class CategorySerilaizer(serializers.ModelSerializer):

    class Meta:
        model =  Category
        fields = ('id','category_name','slug','description')


class PostUserSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)


class PostSerializers(serializers.ModelSerializer):
    user = PostUserSerializer(read_only=True)
    views = serializers.IntegerField(read_only=True)
    category_details = CategorySerilaizer(read_only=True,required=False,source='category')
    category = serializers.IntegerField(write_only=True)
    post_photo_details = serializers.SerializerMethodField()
    post_photo = serializers.ImageField(allow_null=True, required=False,write_only=True)

    def get_post_photo_details(self,obj):
        request = self.context.get('request')
        if obj.post_photo and request:
            return {
                'orinal': request.build_absolute_uri(obj.post_photo .url) ,
                'medium': request.build_absolute_uri(obj.post_photo.medium.url),
                'large': request.build_absolute_uri(obj.post_photo.large.url) ,
                'thumbnail': request.build_absolute_uri(obj.post_photo.thumbnail.url),
            }
        return None
    
    def create(self, validated_data):
        user = self.context.get('request').user

        category_name = validated_data.pop('category',None)
        if category_name:
            category_instance = Category.objects.get(pk=category_name)
            category = category_instance

        post = Post.objects.create(user=user,category=category,**validated_data)
        return post
    
    def update(self, instance, validated_data):
        
        # delete images
        if 'post_photo' in validated_data and validated_data['post_photo'] is None:
            instance.post_photo.delete(save=False)
            instance.post_photo = None

        category_name = validated_data.pop('category',None)
        
        if category_name:
            category_instance = Category.objects.get(pk=category_name)
            instance.category = category_instance

        return super().update(instance, validated_data)
    

    def validate_title(self, title):
        return re.sub(r'[^\w\s]+', '', title) 

    def validate_post_excerpt(self, post_excerpt):
        return bleach.clean(post_excerpt)

    def validate_post_content(self, post_content):
        return bleach.clean(post_content)

    class Meta:
        model = Post
        fields = ['user','category_details','category','title','slug','post_excerpt','post_content','post_photo','post_photo_details','status','views','publish_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    post = serializers.SlugRelatedField(
        queryset=Post.objects.filter(status='published'),
        slug_field='slug'
    )
    
    def validate_comment(self, comment):
        return bleach.clean(comment)

    def create(self, validated_data):
        user = self.context.get('request').user
        return Comment.objects.create(user=user,**validated_data)    
    

    class Meta:
        model =  Comment
        fields = "__all__"
