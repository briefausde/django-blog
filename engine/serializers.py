from django.contrib.auth.models import User, Group
from .models import Post, Category
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    img = serializers.CharField(source='profile.img')
    description = serializers.CharField(source='profile.description')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'img', 'description')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('url', 'name')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('url', 'pk', 'name', 'text_small', 'text_big',
                  'img_small', 'img_big', 'tags', 'category', 'comments_mode')
