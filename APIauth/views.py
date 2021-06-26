from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User

import jwt,datetime
from os import environ

# Create your views here.
class RegisterView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)



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

        token = jwt.encode(payload, "sdofnsodf", algorithm='HS256')
        res = Response()
        res.set_cookie(key='auth', value=token, httponly=True, expires=payload['exp'])

        res.data = {
            "message" : "Login Success!",
        }
        return res