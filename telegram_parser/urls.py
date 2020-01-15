from django.urls import path

from .views import Index, detailed


urlpatterns = [
    path('', Index.as_view(), name='index_1'),
    path('<page>', Index.as_view(), name='index'),
    path('detailed/<comment_id>', detailed, name='detailed')
    # path('payment', Payment.as_view(), name='payment')
]
