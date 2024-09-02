from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils import timezone
import uuid     ,os
from stdimage import StdImageField
from django_countries.fields import CountryField

year =  timezone.now().year
month =  timezone.now().month 

# show first_name in django-admin and any table return user instance
User.__str__ = lambda instance: instance.first_name

def imageUpload_main(instance, filename):
    uuid_token = uuid.uuid4().hex
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid_token}{ext}"
    return f"profile/main_images/{year}/{month}/{new_filename}"


def imageUpload_cover(instance, filename):
    uuid_token = uuid.uuid4().hex
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid_token}{ext}"
    return f"profile/cover_images/{year}/{month}/{new_filename}"


class Profile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(verbose_name=_('Gender'),max_length=6,choices=GENDER_CHOICES)
    country = CountryField(verbose_name=_('Country'),blank=True,null=True)
    work = models.CharField(verbose_name=_('Work'),max_length=50,blank=True,null=True)
    phone = models.CharField(verbose_name=_('Phone'),max_length=15,blank=True,null=True)
    education = models.CharField(verbose_name=_('Education'),max_length=50,blank=True,null=True)
    main_photo = StdImageField(verbose_name=_('Main Image'),upload_to=imageUpload_main, blank=True, null=True, variations={
        'large': (600, 400),
        'thumbnail': (100, 100, True),
        'medium': (300, 200),
    }, delete_orphans=True)
    cover_photo = StdImageField(verbose_name=_('Cover Image'),upload_to=imageUpload_main, blank=True, null=True, variations={
        'large': (600, 400),
        'thumbnail': (100, 100, True),
        'medium': (300, 200),
    }, delete_orphans=True)
    bio = models.TextField(verbose_name=_('Bio'),max_length=500,blank=True,null=True)
    last_modified = models.DateTimeField(verbose_name=_('Last Modified'),auto_now=True,blank=True,null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"