from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.serializers import CountryFieldMixin

from .models import Profile
from django.contrib.auth import authenticate, get_user_model

import re ,bleach

UserModel = get_user_model()

################## custom register #####################
try:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.models import  EmailAddress
    from allauth.utils import get_username_max_length
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=get_username_max_length(),min_length=3,required=True) # max_length of django = 150
    first_name = serializers.CharField(max_length=50,min_length=2,required=True)
    last_name = serializers.CharField(max_length=50,min_length=2,required=True)
    email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    # remove : spaces, special characters (like @, #, $, etc.), punctuation marks, and symbols and _ and 0-9
    def validate_first_name(self,first_name):
        return re.sub(r'[\W_0-9]+', '', first_name) 

    def validate_last_name(self,last_name):
        return re.sub(r'[\W_0-9]+', '', last_name) 

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if email and EmailAddress.objects.is_verified(email):
                raise serializers.ValidationError(
                    _('A user is already registered with this e-mail address.'),
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
################## end custom register #####################

################## custom UserDetailsSerializer #####################

class UserDetailsSerializer(serializers.ModelSerializer):
    
    """User model w/o password"""

    @staticmethod
    def validate_username(username):
        if 'allauth.account' not in settings.INSTALLED_APPS:
            # We don't need to call the all-auth
            # username validator unless its installed
            return username

        from allauth.account.adapter import get_adapter
        username = get_adapter().clean_username(username)
        return username

    # remove : spaces, special characters (like @, #, $, etc.), punctuation marks, and symbols and _ and 0-9
    def validate_first_name(self,first_name):
        return re.sub(r'[\W_0-9]+', '', first_name) 

    def validate_last_name(self,last_name):
        return re.sub(r'[\W_0-9]+', '', last_name) 

    class Meta:
        extra_fields = []
        # see https://github.com/iMerica/dj-rest-auth/issues/181
        # UserModel.XYZ causing attribute error while importing other
        # classes from `serializers.py`. So, we need to check whether the auth model has
        # the attribute or not
        if hasattr(UserModel, 'USERNAME_FIELD'):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, 'EMAIL_FIELD'):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, 'first_name'):
            extra_fields.append('first_name')
        if hasattr(UserModel, 'last_name'):
            extra_fields.append('last_name')
        model = UserModel
        fields = ('pk', *extra_fields)
        read_only_fields = ('email',)

################## end custom UserDetailsSerializer #####################





################## profile #####################
class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

class ProfileSerializer(CountryFieldMixin,serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    main_photo = serializers.ImageField(write_only=True,allow_null=True,required=False)
    cover_photo = serializers.ImageField(write_only=True,allow_null=True,required=False)

    main_photo_details = serializers.SerializerMethodField()
    cover_photo_details = serializers.SerializerMethodField()

    def get_main_photo_details(self,obj):
        request = self.context.get('request')
        if obj.main_photo and request:
            return {
                'orinal': request.build_absolute_uri(obj.main_photo .url) ,
                'medium': request.build_absolute_uri(obj.main_photo.medium.url),
                'large': request.build_absolute_uri(obj.main_photo.large.url) ,
                'thumbnail': request.build_absolute_uri(obj.main_photo.thumbnail.url),
            }
        return None

    def get_cover_photo_details(self,obj):
        request = self.context.get('request')
        if obj.cover_photo and request:
            return {
                'orinal': request.build_absolute_uri(obj.cover_photo .url) ,
                'medium': request.build_absolute_uri(obj.cover_photo.medium.url),
                'large': request.build_absolute_uri(obj.cover_photo.large.url) ,
                'thumbnail': request.build_absolute_uri(obj.cover_photo.thumbnail.url),
            }
        return None


    def update(self, instance, validated_data):
        if 'main_photo' in validated_data and validated_data['main_photo'] is None:
            instance.main_photo.delete(save=False)
            instance.main_photo = None

        if 'cover_photo' in validated_data and validated_data['cover_photo'] is None:
            instance.cover_photo.delete(save=False)
            instance.cover_photo = None
        
        # remove : spaces, special characters (like @, #, $, etc.), punctuation marks, and symbols and _ and 0-9
        if validated_data.get('work') != None:
            validated_data['work'] = re.sub(r'[^\w\s]+', '', validated_data['work']) 

        if validated_data.get('education') != None:
            validated_data['education'] = re.sub(r'[^\w\s]+', '', validated_data['education']) 

        if validated_data.get('bio') != None:
            validated_data['bio'] = bleach.clean(validated_data['bio'])

        return super().update(instance, validated_data)

    class Meta:
        model = Profile
        exclude = ('id',"last_modified")
