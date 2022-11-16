from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .decorators import twitter_login_required
from .models import TwitterAuthToken, TwitterUser, ImageModel
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
from .serializers import ImageSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ImageSearchBytag(generics.ListAPIView):
    serializer_class = ImageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = ImageModel.objects.all()
        limit = self.request.query_params.get('limit')
        word = self.request.query_params.get('word')
        order = self.request.query_params.get('order')
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
        if order == "new":
            queryset = queryset.order_by('id').reverse()
        if limit is not None:
            queryset = queryset[:int(limit)]

        return queryset


class Imagelist(generics.RetrieveAPIView):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()


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
        newimg = ImageModel(title=request.data['title'], image=request.data['image'],
                            prompt=request.data['prompt'], neg_prompt=request.data['neg_prompt'], additonal_tags=request.data['additonal_tags'],
                            decription=request.data['decription'], good=request.data['good'], is_nsfw=request.data['is_nsfw'], seed=request.data['seed'])
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
                    return redirect("http://localhost:8080/#/about/?t="+token.key+"&id="+str(user.id))
                    return JsonResponse({'token': token.key})
            else:
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return redirect('http://localhost:8080')
       # return render(request, 'server/error_page.html')
        else:
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return redirect('http://localhost:8080')
       # return render(request, 'server/error_page.html')
    else:
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return redirect('http://localhost:8080')
       # return render(request, 'server/error_page.html')


@login_required
@twitter_login_required
def index(request):
    return render(request, 'server/home.html')


@login_required
def twitter_logout(request):
    logout(request)
    return redirect('index')


def index(request):
    return HttpResponse('文字だけアプリ改変テスト')


@login_required
def tamesi(request):
  #  print("USER")
  #  print(vars(request))
  #  print(request.user)
    return HttpResponse('ログイン必要テスト')
