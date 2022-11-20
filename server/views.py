from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .decorators import twitter_login_required
from .models import *
from .authorization import create_update_user_from_twitter, check_token_still_valid
from twitter_api.twitter_api import TwitterAPI
from rest_framework import generics, permissions
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.social_serializers import TwitterLoginSerializer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .authorization import ExampleAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import *
# from django.contrib.auth.models import User
from .models import CustomUser
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class ImageRetriveFromUserid(generics.ListAPIView):
    serializer_class = ImageSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = ImageModel.objects.all()
        limit = self.request.query_params.get('limit')
        user_id = self.request.query_params.get('user_id')

        if user_id is not None:
            queryset = queryset.filter(author_id_id=user_id)
        if limit is not None:
            queryset = queryset[:int(limit)]
        return queryset


class UserRetrieve(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserTwitter(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserTwitterSerializer

    def get(self, request, pk):
        user = CustomUser.objects.filter(id=pk).select_related("twitteruser").first()

        data = {
            "screenname":  user.twitteruser.screen_name,
            "profile_image_url": user.twitteruser.profile_image_url,
            "last_name": user.last_name,

        }
        return JsonResponse(data)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ImageSearchBytag_nopage(generics.ListAPIView):
    serializer_class = ImageSerializer

    def get_queryset(self):
        queryset = ImageModel.objects.select_related("author_id")
        limit = self.request.query_params.get('limit')
        word = self.request.query_params.get('word')
        order = self.request.query_params.get('order')
        start = self.request.query_params.get('start')
        nsfw = self.request.query_params.get('nsfw')
        end = self.request.query_params.get('end')
        author_id = self.request.query_params.get('author_id')
        if nsfw is not None and nsfw != "-1":
            queryset = queryset.filter(is_nsfw=nsfw)
        if author_id is not None:
            queryset = queryset.filter(author_id_id=author_id)
        if start is not None:
            start = int(start)
            queryset = queryset.filter(id__gte=start)
        if end is not None:
            end = int(end)
            queryset = queryset.filter(id__lte=end)
        if word is not None:
            queryset = queryset.filter(
                Q(title__contains=word) |
                Q(decription__contains=word) |
                Q(additonal_tags__contains=word) |
                Q(prompt__contains=word) |
                Q(neg_prompt__contains=word)
            )
        if order == "new":
            queryset = queryset.order_by('id').reverse()
        elif order == "popular":
            queryset = queryset.order_by('good').reverse()
        elif order == "today_popular":
            queryset = queryset.order_by('today_good').reverse()
        elif order == "today_popular_looked":
            queryset = queryset.order_by('today_looked').reverse()
        elif order == "hour_popular":
            queryset = queryset.order_by('hour_good').reverse()
        elif order == "hour_popular_looked":
            queryset = queryset.order_by('hour_looked').reverse()
        else:
            queryset = queryset.order_by('id')
        if limit is not None:
            queryset = queryset[:int(limit)]
        return queryset


class ImageSearchBytag(generics.ListAPIView):
    serializer_class = ImageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = ImageModel.objects.select_related("author_id")
        limit = self.request.query_params.get('limit')
        word = self.request.query_params.get('word')
        order = self.request.query_params.get('order')
        start = self.request.query_params.get('start')
        nsfw = self.request.query_params.get('nsfw')
        end = self.request.query_params.get('end')
        author_id = self.request.query_params.get('author_id')
        if nsfw is not None and nsfw != "-1":
            queryset = queryset.filter(is_nsfw=nsfw)
        if author_id is not None:
            queryset = queryset.filter(author_id_id=author_id)
        if start is not None:
            start = int(start)
            queryset = queryset.filter(id__gte=start)
        if end is not None:
            end = int(end)
            queryset = queryset.filter(id__lte=end)
        if word is not None:
            queryset = queryset.filter(
                Q(title__contains=word) |
                Q(decription__contains=word) |
                Q(additonal_tags__contains=word) |
                Q(prompt__contains=word) |
                Q(neg_prompt__contains=word)
            )
        if order == "new":
            queryset = queryset.order_by('id').reverse()
        elif order == "popular":
            queryset = queryset.order_by('good').reverse()
        elif order == "today_popular":
            queryset = queryset.order_by('today_good').reverse()
        elif order == "today_popular_looked":
            queryset = queryset.order_by('today_looked').reverse()
        elif order == "hour_popular":
            queryset = queryset.order_by('hour_good').reverse()
        elif order == "hour_popular_looked":
            queryset = queryset.order_by('hour_looked').reverse()
        else:
            queryset = queryset.order_by('id')
        if limit is not None:
            queryset = queryset[:int(limit)]
        return queryset


class UserFavRetriveView(generics.RetrieveAPIView):
    serializer_class = UserFavSerializer
    queryset = CustomUser.objects.all()

    def get_queryset(self):
        user = CustomUser.objects.filter(id=self.kwargs['pk']).prefetch_related("fav")
        print(user.values('id', 'username', 'first_name', 'fav', 'description', 'profile_url'))
        return user


class GetFavorite(generics.ListAPIView):
    authentication_classes = (ExampleAuthentication,)        # 追加
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = {}
        user = request.user
        for fav in user.fav.all():
            data[fav.image.id] = fav.image.title
        return JsonResponse(data)


class GetFavoritebyAuthorId(APIView):
    authentication_classes = (ExampleAuthentication,)        # 追加
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        data = {}
        # print(vars(user))
        for fav in user.fav.all():
            if int(fav.image.author_id_id) == int(pk):
                data[fav.image.id] = fav.image.title
        return JsonResponse(data)


class MyFollow(APIView):
    authentication_classes = (ExampleAuthentication,)        # 追加
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        data = {}
        for follow in user.following_user.all():
            data[follow.followed_user.id] = True
        return JsonResponse(data)


class Follow(APIView):
    authentication_classes = (ExampleAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        followed_user = CustomUser.objects.get(id=pk)
        myfollow = FollowUser(followed_user=followed_user, following_user=user)
        if FollowUser.objects.filter(followed_user=followed_user, following_user=user).exists():
            return JsonResponse({"status": "already exists"})
        myfollow.save()
        return HttpResponse(status=200)


class UnFollow(APIView):
    authentication_classes = (ExampleAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        followed_user = CustomUser.objects.get(id=pk)
        myfollow = FollowUser.objects.filter(followed_user=followed_user, following_user=user)
        myfollow.delete()
        return HttpResponse(status=200)


class FavCreateView(APIView):
    authentication_classes = (ExampleAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        image = ImageModel.objects.get(id=pk)
        if (FavImage.objects.filter(image=image, user=user).exists()):
            return JsonResponse({"message": "already exist"})
        fav = FavImage(user=user, image=image)
        fav.save()
        image.good += 1
        image.today_good += 1
        image.hour_good += 1
        image.save()
        return HttpResponse(status=200)


class FavDeleteView(APIView):
    authentication_classes = (ExampleAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        image = ImageModel.objects.get(id=pk)
        fav = FavImage.objects.get(user=user, image=image)
        fav.delete()
        image.good -= 1
        image.save()
        return HttpResponse(status=200)


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer
    queryset = CommentImage.objects.all()
    authentication_classes = (ExampleAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        image = ImageModel.objects.get(id=request.data['image_id'])
        comment = CommentImage(user=user, image=image, comment=request.data['comment'])
        comment.save()
        return HttpResponse(status=200)


class GetImageComment(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        image = ImageModel.objects.get(id=pk)
        comments = image.comment_image.all().order_by('id').reverse()
        return comments


class Imagelist(generics.RetrieveAPIView):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()


class ImageDelete(APIView):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()
    authentication_classes = (ExampleAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        image = ImageModel.objects.get(id=pk)
        if image.author_id != request.user:


x
            return HttpResponse(status=401)

        image.delete()
        return HttpResponse(status=200)


class ImageCreate(generics.CreateAPIView):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()
    authentication_classes = (ExampleAuthentication,)        # 追加
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print("post")
        if request.data['prompt'] == "undefined":
            request.data['prompt'] = "入力がありません。"
        if request.data['neg_prompt'] == "undefined":
            request.data['neg_prompt'] = "入力がありません。"
        if request.data['additonal_tags'] == "undefined":
            request.data['additonal_tags'] = ""
        else:
            tags = [None, None, None, None, None, None, None, None, None, None]
            buf_tags = request.data['additonal_tags'].split(',')
            for i, tag in enumerate(buf_tags):
                if (tag == ""):
                    continue
                tags[i] = tag
        newimg = ImageModel(title=request.data['title'], image=request.data['image'],
                            prompt=request.data['prompt'], neg_prompt=request.data['neg_prompt'], additonal_tags=request.data['additonal_tags'],
                            decription=request.data['decription'], good=request.data['good'], is_nsfw=request.data['is_nsfw'], seed=request.data['seed'],
                            tag0=tags[0], tag1=tags[1], tag2=tags[2], tag3=tags[3], tag4=tags[4], tag5=tags[5], tag6=tags[6], tag7=tags[7], tag8=tags[8], tag9=tags[9])
        newimg.author_id_id = request.user.id
        newimg.save()

        return JsonResponse({'newid': newimg.id})
        print("DATA")
        print(request.data)
        request.data['author_id_id'] = User.objects.get(id=request.user.id)
        print(request.data)
       # print(request.data)
        serializer = ImageSerializer(data=request.data)
        # print(vars(serializer))
       # serializer = ImageSerializer(serializer, data={'author_id_id': request.user.id}, partial=True)
        serializer.created_by = request.user
        serializer.author_id_id = request.user
        if serializer.is_valid():
            print("OK")
            serializer.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors)
  #  permission_classes = (IsAuthenticated,)
  #  authentication_classes = (ExampleAuthentication,)


class ImageSearchBytag_count(APIView):
    serializer_class = ImageSerializer

    def get(self, request):
        queryset = ImageModel.objects.all()
        limit = self.request.query_params.get('limit')
        word = self.request.query_params.get('word')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start is not None:
            start = int(start)
            queryset = queryset.filter(id__gte=start)
        if end is not None:
            end = int(end)
            queryset = queryset.filter(id__lte=end)
        if word is not None:
            queryset = queryset.filter(
                Q(title__contains=word) |
                Q(decription__contains=word) |
                Q(additonal_tags__contains=word)
            )

        if limit is not None:
            queryset = queryset[:int(limit)]

        return JsonResponse({'num': queryset.count()})


class YesMan(APIView):
    authentication_classes = (ExampleAuthentication,)        # 追加
    permission_classes = (IsAuthenticated,)                  # 追加

    def post(self, request, format=None):
        print(request.user)
        return JsonResponse({'message': request.user.id})


class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter


def is_login(request):
    data = {
        "res":  request.user.is_authenticated
    }
    print(request.user)
    return JsonResponse(data=data)


# Create your views here.
def twitter_login(request):

    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    print("HERE")
    print(url)
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, 'server/error_page.html')
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        print("TWITTER AUTH TOKEN")
        print(twitter_auth_token)
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)

            twitter_auth_token.save()
        else:
            twitter_auth_token.oauth_token_secret = oauth_token_secret

            twitter_auth_token.save()
        print("REDIRECT")
        print(url)
        return redirect(url)


def twitter_callback(request):
    print("HERE")
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return redirect('index')
       # return render(request, 'server/error_page.html')
    twitter_api = TwitterAPI()
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    print("HERE")
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        if access_token is not None and access_token_secret is not None:
            twitter_auth_token.oauth_token = access_token
            twitter_auth_token.oauth_token_secret = access_token_secret
            TwitterAuthToken.objects.filter(oauth_token=access_token).delete()
            twitter_auth_token.save()
            # Create user
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                print(info[0]['id'])
                print(info[0]['profile_image_url'])
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'],
                                               name=info[0]['name'], profile_image_url=info[0]['profile_image_url'])
                twitter_user_new.twitter_oauth_token = twitter_auth_token
                user, twitter_user = create_update_user_from_twitter(twitter_user_new)
                if user is not None:
                    token, res = Token.objects.get_or_create(user=user)
                    return redirect(settings.REDIRECT+"/#/about/?t="+token.key+"&id="+str(user.id))
                    return JsonResponse({'token': token.key})
            else:
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return redirect(settings.REDIRECT)
       # return render(request, 'server/error_page.html')
        else:
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return redirect(settings.REDIRECT)
       # return render(request, 'server/error_page.html')
    else:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return redirect(settings.REDIRECT)
       # return render(request, 'server/error_page.html')


class UpdateMyInfo(APIView):
    authentication_classes = (ExampleAuthentication,)        # 追加
    permission_classes = (IsAuthenticated,)                  # 追加

    def post(self, request, format=None):
        user = request.user
        new_description = request.data.get('description')
        id = request.data.get('id')
        print(new_description)
        if id is None or id != user.id:
            return JsonResponse({'message': 'id is not correct'})
        if new_description is not None:
            user.description = new_description
        user.save()
        return JsonResponse({'message': 'success'})


@ login_required
@ twitter_login_required
def index(request):
    return render(request, 'server/home.html')


@ login_required
def twitter_logout(request):
    logout(request)
    return redirect('index')


def index(request):
    return HttpResponse('文字だけアプリ')


@ login_required
def tamesi(request):
  #  print("USER")
  #  print(vars(request))
  #  print(request.user)
    return HttpResponse('ログイン必要テスト')
