from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import TelegramParserComment
from users.models import Profile
from django.contrib import messages


class Index(View):
    def get(self, request, page=1):
        data = request.GET
        print(data)
        page = int(page)
        filter_data = {key: item for key, item in data.items() if item != ''}
        # Filter dictionary copy to fill form
        fill_data = filter_data.copy()
        comments = TelegramParserComment.objects.all()

        if 'search' in filter_data and len(filter_data.get('search')) > 0:
            search = filter_data.pop('search')
            page = 1
            try:
                searchtype = filter_data.pop('searchtype')
                if searchtype == 'short':
                    comments = comments.filter(short__contains=search)
                else:
                    # comments
                    pass
            except KeyError as keyerr:
                print(keyerr)
                messages.info(request, 'Тип поиска не указан')
        elif 'search' not in filter_data and 'searchtype' in filter_data:
            filter_data.pop('searchtype')
            messages.info(request, 'Пустая строка поиска')

        if len(filter_data) > 0:
            comments = comments.filter(**filter_data)
        pagelist = list(range(1, int(len(comments) / 30)))

        # Applying page interval
        if len(comments) > 30:
            comments = comments[30 * page-30:30 * page]

        if len(comments) == 0:
            messages.warning(request, 'Отзывов не найдено')
        context = {
            'title': 'Комментарии',
            'comments': comments,
            'pagelist': pagelist,
            'filldata': fill_data
        }
        return render(request, 'parser/mainpage.html', context)

    def post(self, request):
        data = request.POST
        context = {
            'title': 'Комментарии'
        }
        return render(request, 'parser/mainpage.html', context)

# ! Deprecated, left for info purposes
    # def deprecated(self, request):
    #     data = dict(request.GET)
    #     print(data)
    #     data = {key: item[0] for key, item in data.items() if item != ['']}
    #     print(data)
    #     comments = TelegramParserComment.objects.filter(**data)
    #     pagelist = list(range(1, int(len(comments) / 30)))

    #     # Pagination
    #     if 'page' in data:
    #         interval = 30 * int(data.get('page')[0])

    #         try:
    #             comments = comments[interval - 30:interval]
    #         except Exception as e:
    #             comments = comments[:30]
    #             data['page'] = 1
    #     else:
    #         comments = comments[:30]
    #         data['page'] = 1

    #     context = {
    #         'title': 'Комментарии',
    #         'comments': comments,
    #         'pagelist': pagelist
    #     }
    #     return render(request, 'parser/mainpage.html', context)
    

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
