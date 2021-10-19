from django.urls import path
from .views import startBacktestUtil, OHLCData, deposit, withdraw
urlpatterns = [
    path('start/', startBacktestUtil),
    path('ohlc/', OHLCData),
    path('deposit/', deposit),
    path('withdraw/', withdraw),
]   
