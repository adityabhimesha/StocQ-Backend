from django.urls import path,include
from .views import RegisterView
from .views import LoginView
from .views import UserView
from .views import LogoutView
 
urlpatterns = [
     path('register/', RegisterView.as_view(), name="register"),
     path('login/', LoginView.as_view(), name="login"),
     path('logout/', LogoutView.as_view(), name="logout"),
     path('', UserView.as_view(), name="home"),
]   
