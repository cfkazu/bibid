from django.db import models
# Create your models here.


class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255, null=True)
    oauth_token_secret = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.oauth_token


class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.screen_name


class ImageModel(models.Model):
    author_id = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    #author_id = models.IntegerField()
    title = models.CharField(max_length=30)
    image = models.ImageField(upload_to='')
    prompt = models.TextField(default="入力されていません")
    neg_prompt = models.TextField(default="入力されていません")
    additonal_tags = models.TextField(default="入力されていません")
    decription = models.TextField()
    good = models.IntegerField(default=0)
    is_nsfw = models.IntegerField(default=False)
    seed = models.IntegerField(default=-1)
