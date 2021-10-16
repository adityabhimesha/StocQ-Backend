from django.urls import path,include
from .views import startBacktestUtil
urlpatterns = [
    path('start/', startBacktestUtil)
]   
