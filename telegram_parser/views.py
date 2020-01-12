from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import TelegramParserComment
from users.models import Profile
from .liq_sdk import LiqPay


class Index(View):
    def get(self, request):
        data = request.GET
        comments = TelegramParserComment.objects.all()

        if 'page' in data:
            interval = 30 * int(data['page'])
            comments = TelegramParserComment.objects.all()[interval - 30:interval]
        context = {
            'title': 'Комментарии',
            'comments': comments
        }
        # pages = 
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
        liqpay = LiqPay(
            'sandbox_i41551166851',
            'sandbox_TQuWlo3gIC9Vz9fchAq9qrdPGJz3segJzpNpD1N7'
        )
        form = liqpay.cnb_form({
            "action": "hold",
            "amount": "99",
            "currency": "UAH",
            "description": f"Premium account(1 month) for user",
            "order_id": "order_id_2",
            "version": "3"
        })
        context = {
            'title': 'Оплата',
            'form': form
        }
        return render(request, 'paymentpage.html', context)
