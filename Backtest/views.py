from django.shortcuts import render
from django.http import HttpResponse
from DQN.predict import startBacktest
import json
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from APIauth.models import User
from os import environ
import jwt

# Create your views here.
def startBacktestUtil(request):

    token = request.COOKIES.get('auth')
    if not token:
        raise AuthenticationFailed('User Not Authenticated!')

    try:
        payload = jwt.decode(token, environ['SECRET'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User Not Authenticated!!!')

    user_id = payload['id']
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        raise AuthenticationFailed('User Does Not Exist!') 


    key = request.GET['stock_name']
    if(key == ""):
        payload = {
            "message" : "Please Pick a Stock!"
        }
        return HttpResponse(json.dumps(payload),status=400, content_type="application/json")


    agent = startBacktest(initial_balance=user.balance, stock_name=key)

    user.balance = agent.balance
    user.save()


    payload = {
        "portfolio_values" : agent.portfolio_values,
        "return_rates" : agent.return_rates,
        "buy_dates" : agent.buy_dates,
        "sell_dates" : agent.sell_dates,
        "initial_portfolio_value" : agent.initial_portfolio_value,
        "balance" : agent.balance,
        "inventory" : agent.inventory,
        "profits" : agent.profits,
    }
    
    return HttpResponse(json.dumps(payload), content_type="application/json")


def OHLCData(request):
    prices = []
    key = request.GET['stock_name']
    lines = open("DQN/data/" + key + ".csv", "r").read().splitlines()
    for line in lines[1:]:
        data = []

        data.append(line.split(",")[0])
        data.append(line.split(",")[1])
        data.append(line.split(",")[2])
        data.append(line.split(",")[3])
        data.append(line.split(",")[4])
        data.append(line.split(",")[5])
        data.append(line.split(",")[6])

        prices.append(data)

    payload = {
        "data" : prices
    }

    return HttpResponse(json.dumps(payload), content_type="application/json")

def getBalance(request):
    token = request.COOKIES.get('auth')


    payload = jwt.decode(token, environ['SECRET'], algorithms=['HS256'])

    user_id = payload['id']
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        raise AuthenticationFailed('User Does Not Exist!') 

    payload = {
        "username" : user.name,
        "balance" : user.balance,
    }

    return HttpResponse(json.dumps(payload), content_type="application/json")
    

def deposit(request):
    token = request.COOKIES.get('auth')
    if not token:
        raise AuthenticationFailed('User Not Authenticated!')

    try:
        payload = jwt.decode(token, environ['SECRET'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User Not Authenticated!!!')

    user_id = payload['id']
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        raise AuthenticationFailed('User Does Not Exist!') 

    
    amount = int(request.GET['amount'])
    if(amount <= 0):
        return HttpResponse('Amount should be greater than 0',status=500, content_type="application/json")

    user.balance += amount
    user.save()

    payload = {
        "username" : user.name,
        "balance" : user.balance,
    }

    return HttpResponse(json.dumps(payload), content_type="application/json")

def withdraw(request):
    token = request.COOKIES.get('auth')
    if not token:
        raise AuthenticationFailed('User Not Authenticated!')

    try:
        payload = jwt.decode(token, environ['SECRET'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('User Not Authenticated!!!')

    user_id = payload['id']
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        raise AuthenticationFailed('User Does Not Exist!') 

    
    amount = int(request.GET['amount'])
    if(amount <= 0):
        return HttpResponse('Amount should be greater than 0',status=500, content_type="application/json")

    if(amount > user.balance):
        return HttpResponse('Amount cannot be greater than your balance',status=500, content_type="application/json")

    user.balance -= amount
    user.save()

    payload = {
        "username" : user.name,
        "balance" : user.balance,
    }

    return HttpResponse(json.dumps(payload), content_type="application/json")