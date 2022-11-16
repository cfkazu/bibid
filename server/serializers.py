from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ImageModel, TwitterUser


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ('id', 'title', 'image', 'prompt', 'neg_prompt', 'additonal_tags', 'decription', 'good', 'author_id_id', 'is_nsfw', 'seed')


class TwitterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterUser
        fields = ('id', 'twitter_id', 'screen_name', 'name', 'profile_image_url',)


class UserTwitterSerializer(serializers.ModelSerializer):
    twitter = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'last_name', 'twitter')
