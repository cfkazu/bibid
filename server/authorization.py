from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
from rest_framework.authtoken.models import Token

from twitter_api.twitter_api import TwitterAPI

from .models import TwitterUser

# TODO: ユーザの自己紹介欄をどこかに作る:LastName?150字までだけどどうにかなるか？
# TODO: ユーザのidをもとにユーザ情報を返す。mypageとかで使う


def create_update_user_from_twitter(twitter_user_new):
    twitter_user = TwitterUser.objects.filter(twitter_id=twitter_user_new.twitter_id).first()
    if twitter_user is None:
        user = User.objects.filter(username=twitter_user_new.screen_name).first()
        if user is None:
            user = User(username=twitter_user_new.screen_name,
                        first_name=twitter_user_new.name, email=twitter_user_new.profile_image_url)
            user.save()
        print("image_url")
        print(twitter_user_new.profile_image_url)
        twitter_user = TwitterUser(twitter_id=twitter_user_new.twitter_id,
                                   name=twitter_user_new.name,
                                   screen_name=twitter_user_new.screen_name,
                                   profile_image_url=twitter_user_new.profile_image_url)
        twitter_user.user = user
        user.last_name = twitter_user_new.profile_image_url
        user.save()
        twitter_user.twitter_oauth_token = twitter_user_new.twitter_oauth_token
        twitter_user.save()
        return user, twitter_user
    else:
        print("image_url")
        print(twitter_user_new.profile_image_url)
        twitter_user.twitter_oauth_token = twitter_user_new.twitter_oauth_token
        twitter_user.screen_name = twitter_user_new.screen_name
        twitter_user.proile_image_url = twitter_user_new.profile_image_url
        user.email = twitter_user_new.profile_image_url
        twitter_user.save()
        user = twitter_user.user
        if user is not None:
            return user, twitter_user
        else:
            return None, twitter_user


def check_token_still_valid(twitter_user):
    twitter_api = TwitterAPI()
    info = twitter_api.get_me(twitter_user.twitter_oauth_token.oauth_token,
                              twitter_user.twitter_oauth_token.oauth_token_secret)
    return info


class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token_key = request.META.get('HTTP_X_AUTH_TOKEN')
        if not token_key:
            # リクエストヘッダにトークンが含まれない場合はエラー
            raise exceptions.AuthenticationFailed({'message': 'token injustice.'})
        token = Token.objects.filter(key=token_key).first()
        if token == None:
            # トークンが存在しない場合はエラー
            raise exceptions.AuthenticationFailed({'message': 'token not found.'})
        return (token.user, None)
