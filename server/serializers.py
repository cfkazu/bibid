from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'description', 'profile_url')


class TwitterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterUser
        fields = ('id', 'twitter_id', 'screen_name', 'name', 'profile_image_url',)


class UserTwitterSerializer(serializers.ModelSerializer):
    twitter = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    image = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'twitter', 'image', 'profile_url', 'description')


class ImageSerializer(serializers.ModelSerializer):
    author_id = UserTwitterSerializer()

    class Meta:
        model = ImageModel
     #   fields = ('id', 'title', 'image', 'prompt', 'neg_prompt', 'additonal_tags', 'decription', 'good', 'author_id_id', 'is_nsfw', 'seed', 'author')
        fields = '__all__'


class FavSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    user = UserSerializer()

    class Meta:
        model = FavImage
        fields = ('id', 'image', 'user')


class FavOidSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavImage
        fields = ('image',)


class UserFavSerializer(serializers.ModelSerializer):
    fav = FavOidSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'fav', 'profile_url', 'description')


class FollowUserSerializer(serializers.ModelSerializer):
    followed_user = UserSerializer()
    follower_user = UserSerializer()

    class Meta:
        model = FollowUser
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = CommentImage
        fields = '__all__'
