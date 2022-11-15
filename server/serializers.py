from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ImageModel


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ('id', 'title', 'image', 'prompt', 'neg_prompt', 'additonal_tags', 'decription', 'good', 'author_id_id', 'is_nsfw', 'seed')
