from django.urls import path, re_path, include
from . import views
from server.views import TwitterLogin
from .views import *
urlpatterns = [
    path('', views.index, name='index'),
    path('logintest', views.tamesi, name='logintest'),
    path('twitter_login/', views.twitter_login, name='twitter_loginbak'),
    path('twitter_callback/', views.twitter_callback, name='twitter_callbackbak'),
    path('twitter_logout/', views.twitter_logout, name='twitter_logoutbak'),
    path('islogin', views.is_login, name='islogin'),
    path('yesman', YesMan.as_view()),
    path('getgraph/<pk>/', Imagelist.as_view()),
    path('creategraph/', ImageCreate.as_view(), name='creategraph'),
    path('searchbyword/', ImageSearchBytag.as_view(), name='searchbyword'),
    path('getsearchressize/', ImageSearchBytag_count.as_view()),
    # path('getuser/<pk>', UserandTwitterRetrieveAPIVIew.as_view()),
]
