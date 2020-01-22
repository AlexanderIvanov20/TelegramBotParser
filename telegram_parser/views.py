from django.views import View
from users.models import Profile
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import TelegramParserComment


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
                    comments = comments.filter(short__icontains=search)
                elif searchtype == 'initials':
                    comments = comments.filter(
                        Q(customer__icontains=search) | Q(
                            recipient__icontains=search)
                    )
                elif searchtype == 'links':
                    comments = comments.filter(
                        Q(customer_link__icontains=search) | Q(
                            recipient_link__icontains=search)
                    )
                else:
                    comments = []
                    messages.error(request, 'Блэт')
            except KeyError as keyerr:
                messages.info(request, 'Тип поиска не указан')

        elif 'search' not in filter_data and 'searchtype' in filter_data:
            filter_data.pop('searchtype')
            messages.info(request, 'Пустая строка поиска')

        if 'sort_by' in filter_data:
            comments = comments.order_by(filter_data.pop('sort_by'))

        if len(filter_data) > 0:
            comments = comments.filter(**filter_data)

        # Applying page interval
        if len(comments) > 30:
            comments = comments[30 * page-30:30 * page]
        elif len(comments) == 0:
            messages.warning(request, 'Отзывов не найдено')

        pagelist = list(range(1, int(len(comments) / 30)))

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


def detailed(request, comment_id):
    comment = TelegramParserComment.objects.get(id=int(comment_id))
    context = {
        'title': 'Комментарий',
        'comment': comment
    }
    return render(request, 'parser/detailed.html', context)

