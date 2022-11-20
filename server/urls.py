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
    path('searchbyword_nopage/', ImageSearchBytag_nopage.as_view(), name='searchbyword_nopage'),
    path('getsearchressize/', ImageSearchBytag_count.as_view()),
    path('getuser/<pk>', UserRetrieve.as_view()),
    path('modifyme/', UpdateMyInfo.as_view()),
    path('getImagebyUserid/', ImageRetriveFromUserid.as_view()),
    path('fav/<pk>', FavCreateView.as_view()),
    path('delfav/<pk>', FavDeleteView.as_view()),
    path('userfav/<pk>', UserFavRetriveView.as_view()),
    path('getfavoritebyUserid/<pk>', GetFavoritebyAuthorId.as_view()),
    path('getfavorite', GetFavorite.as_view()),
    path('getfollowing/', MyFollow.as_view()),
    path('follow/<pk>', Follow.as_view()),
    path('unfollow/<pk>', UnFollow.as_view()),
    path('makecomment/', CommentCreate.as_view()),
    path('getcomment/<pk>', GetImageComment.as_view()),
]
