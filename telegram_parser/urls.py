from django.urls import path
from .views import Index, detailed, Profiles, Payment


urlpatterns = [
    path('', Index.as_view(), name='index_1'),
    path('<page>', Index.as_view(), name='index'),
    path('detailed/<comment_id>', detailed, name='detailed'),
    path('profiles', Profiles.as_view(), name='profiles'),
    path('payment', Payment.as_view(), name='payment')
]
