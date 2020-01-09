from django.views import View
from django.shortcuts import render
from .models import TelegramParserComment


class Index(View):
    def get(self, request):
        data = request.GET
        comments = TelegramParserComment.objects.all()
        context = {
            'title': 'Главная',
            'comments': comments
        }
        return render(request, 'parser/mainpage.html', context)

    def post(self, request):
        data = request.POST
        context = {
            'title': 'Главная'
        }
        return render(request, 'parser/mainpage.html', context)
