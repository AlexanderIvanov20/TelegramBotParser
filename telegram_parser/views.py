from django.shortcuts import render
from django.views import View


class Index(View):
    def get(self, request):
        data = request.GET
        context = {
            'title': 'Главная'
        }
        return render(request, 'parser/mainpage.html', context)

    def post(self, request):
        data = request.POST
        context = {
            'title': 'Главная'
        }
        return render(request, 'parser/mainpage.html', context)
