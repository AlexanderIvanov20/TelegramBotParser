from django.urls import path
from .views import Register, Login, Logout

urlpatterns = [
    path('register', Register.as_view(), name='register'),
    path('authenticate', Login.as_view(), name='authenticate'),
    path('logout', Logout, name='logout')
]
