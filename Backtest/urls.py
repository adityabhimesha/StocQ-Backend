from django.urls import path
from .views import getBalance, startBacktestUtil, OHLCData, deposit, withdraw
urlpatterns = [
    path('start/', startBacktestUtil),
    path('ohlc/', OHLCData),
    path('deposit/', deposit),
    path('withdraw/', withdraw),
    path('balance/', getBalance),
]   
