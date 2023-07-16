from django.shortcuts import render
from rest_framework import generics

from user.serializers import UserSerializer


class RegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer

