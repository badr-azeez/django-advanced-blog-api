# Generated by Django 5.0.8 on 2024-08-07 19:10

import django.db.models.deletion
import django_countries.fields
import stdimage.models
import user_profiles.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last Name')),
                ('gender', models.CharField(max_length=6, verbose_name='Gender')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Country')),
                ('work', models.CharField(blank=True, max_length=256, null=True, verbose_name='Work')),
                ('phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='Phone')),
                ('education', models.CharField(blank=True, max_length=50, null=True, verbose_name='Education')),
                ('main_photo', stdimage.models.StdImageField(blank=True, force_min_size=False, upload_to=user_profiles.models.imageUpload_main, variations={'large': (600, 400), 'medium': (300, 200), 'thumbnail': (100, 100, True)}, verbose_name='Main Image')),
                ('cover_photo', stdimage.models.StdImageField(blank=True, force_min_size=False, upload_to=user_profiles.models.imageUpload_main, variations={'large': (600, 400), 'medium': (300, 200), 'thumbnail': (100, 100, True)}, verbose_name='Cover Image')),
                ('bio', models.TextField(blank=True, max_length=500, null=True, verbose_name='Bio')),
                ('last_modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Last Modified')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
