from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.utils.translation import gettext as _ 
from django.utils import timezone
import uuid     ,os
from stdimage import StdImageField
from django_countries.fields import CountryField

year =  timezone.now().year
month =  timezone.now().month 

# show first_name in django-admin and any table return user instance

def imageUpload_post_image(instance, filename):
    uuid_token = uuid.uuid4().hex
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid_token}{ext}"
    return f"posts/post_image//{year}/{month}/{new_filename}"

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='category_name')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name
    
    class Meta:
        ordering = ['category_name']

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='title',unique=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    title = models.CharField(verbose_name=_('Title'),max_length=60)
    post_excerpt = models.CharField(verbose_name=_('Post Excerpt'),max_length=80)
    post_content = models.TextField(verbose_name=_('Post Content'),max_length=100000)
    post_photo = StdImageField(verbose_name=_('Main Image'),upload_to=imageUpload_post_image, blank=True,null=True, variations={
        'large': (600, 400),
        'thumbnail': (100, 100, True),
        'medium': (300, 200),
    }, delete_orphans=True)
    status = models.CharField(verbose_name=_('Status'),max_length=20, choices=STATUS_CHOICES, default='published')
    views = models.IntegerField(verbose_name=_('Views'),default=0)
    publish_at = models.DateTimeField(verbose_name=_('Publish At'),default=timezone.now)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-publish_at','title']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment =  models.TextField(verbose_name=_('Comment'),max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
    class Meta:
        ordering = ['-created_at']