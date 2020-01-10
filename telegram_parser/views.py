from django.views import View
from django.shortcuts import render
from .models import TelegramParserComment
from users.models import Profile


class Index(View):
    def get(self, request):
        data = request.GET
        comments = TelegramParserComment.objects.all()
        context = {
            'title': 'Комментарии',
            'comments': comments
        }
        return render(request, 'parser/mainpage.html', context)

    def post(self, request):
        data = request.POST
        context = {
            'title': 'Комментарии'
        }
        return render(request, 'parser/mainpage.html', context)


def detailed(request, comment_id):
    comment = TelegramParserComment.objects.get(id=int(comment_id))
    context = {
        'title': 'Комментарий',
        'comment': comment
    }
    return render(request, 'parser/detailed.html', context)


def profiles(request):
    profiles = Profile.objects.all()
    context = {
        'title': 'Профили'
    }
    return render(request, 'parser/profiles.html', context)
