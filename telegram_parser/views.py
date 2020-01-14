from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import TelegramParserComment
from users.models import Profile


class Index(View):
    def get(self, request):
        data = dict(request.GET)
        comments = TelegramParserComment.objects.all()
        pagelist = list(range(1, int(len(comments) / 30)))
        # Pagination
        if 'page' in data:
            interval = 30 * int(data.get('page')[0])
            comments = comments[interval - 30:interval]
        else:
            comments = comments[:30]
            data['page'] = 1

        context = {
            'title': 'Комментарии',
            'comments': comments,
            'pagelist': pagelist
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


class Profiles(View):
    def get(self, request):
        profiles = Profile.objects.all()
        context = {
            'title': 'Профили',
            'profiles': profiles
        }
        return render(request, 'parser/profiles.html', context)


class Payment(View):
    def get(self, request):
        data = request.GET
        if 'id_user' in data:
            profile = get_object_or_404(Profiles, id_user=data.get('id_user'))
        else:
            pass
        context = {
            'title': 'Оплата'
        }
        return render(request, 'paymentpage.html', context)
