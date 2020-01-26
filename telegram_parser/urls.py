from django.urls import path

from .views import Index, detailed, TextEdit


urlpatterns = [
    path('', Index.as_view(), name='index_1'),
    path('page/<page>', Index.as_view(), name='index'),
    path('detailed/<comment_id>', detailed, name='detailed'),
    path('textedit',TextEdit.as_view(), name='textedit')
]
