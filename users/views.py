from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny


# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    username=request.data.get('username')
    password=request.data.get('password')
    email=request.data.get('email')


    if not username or not password:
        return Response({"error":"username and password are required"},status=status.HTTP_400_BAD_REQUEST)
    user=User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    return Response({"message":"User registered successfully"},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username=request.data.get('username')
    password=request.data.get('password')

    user=authenticate(username=username,password=password)

    if user is None:
        return Response({"error":"Invalid credebtials"},status=status.HTTP_401_UNAUTHORIZED)
    refresh=RefreshToken.for_user(user)

    return Response({"access":str(refresh.access_token),
                    "refresh":str(refresh),
                    "message":"Login successful"})
