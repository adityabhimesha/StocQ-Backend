from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User

import jwt,datetime
from os import environ
import json

# Create your views here.
class RegisterView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        payload = {
            'id' : json.dumps(serializer['id'].value),
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat' : datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, environ['SECRET'], algorithm='HS256').decode('utf-8')
        res = Response()
        res.set_cookie(key='auth', value=token, httponly=True, expires=payload['exp'])

        res.data = {
            "message" : "Register Success!",
        }
        return res



class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('Email or Password Incorrect!')

        if not user.check_password(password):
            raise AuthenticationFailed('Email or Password Incorrect!')

        payload = {
            'id' : user.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat' : datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, environ['SECRET'], algorithm='HS256').decode('utf-8')
        res = Response()
        res.set_cookie(key='auth', value=token, httponly=True, expires=payload['exp'])

        res.data = {
            "message" : "Login Success!",
        }
        return res
    
class LogoutView(APIView):
    def post(self, request, format=None):
        res = Response()
        res.delete_cookie('auth')
        res.data = {
            "message" : "Logout Success!"
        }

        return res



class UserView(APIView):
    def get(self, request, format=None):
        token = request.COOKIES.get('auth')
        if not token:
            raise AuthenticationFailed('User Not Authenticated!')

        try:
            payload = jwt.decode(token, environ['SECRET'], algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Not Authenticated!!!')

        user_id = payload['id']
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            raise AuthenticationFailed('User Does Not Exist!') 

        
        return Response({
            "username" : user.name,
        })