
from django.urls import path
from .views import *

urlpatterns = [
    path('loginapi/', UserLoginapi.as_view(), name='loginapi'),
    path('logout/', Logout.as_view(), name='lgout'),
    path('register', UserprofileListCreateAPIView.as_view(), name='userprofile-list-create'),
]
