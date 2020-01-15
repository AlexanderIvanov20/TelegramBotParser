from django.urls import path

from .views import Register, Login, Logout, Profiles, DetailedProfile

urlpatterns = [
    path('register', Register.as_view(), name='register'),
    path('authenticate', Login.as_view(), name='authenticate'),
    path('logout', Logout, name='logout'),

    path('profiles', Profiles.as_view(), name='profiles'),
    path('profile/<id_user>', DetailedProfile.as_view(), name='profile_detailed')
]
