from django.urls import path
from .views import Index, detailed, profiles


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('detailed/<comment_id>', detailed, name='detailed'),
    path('profiles', profiles, name='profiles')
]
