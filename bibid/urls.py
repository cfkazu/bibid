from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from django.conf import settings
from server.views import TwitterLogin
from django.conf.urls.static import static
urlpatterns = [
    path('', include('server.urls')),
    path('server/', include('server.urls')),
    #   path('admin/', admin.site.urls),
    re_path(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    re_path(r'^dj-rest-auth/twitter/$', TwitterLogin.as_view(), name='twitter_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
