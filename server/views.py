from django.http import HttpResponse


def index(request):
    return HttpResponse('文字だけアプリ改変テスト')
