from django.shortcuts import render
from django.http import HttpResponse
from DQN.predict import startBacktest

# Create your views here.
def startBacktestUtil(request):
    agent = startBacktest(initial_balance=50000)

    return HttpResponse(agent.balance)
