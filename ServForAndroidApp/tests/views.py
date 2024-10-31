from django.shortcuts import render

from .models import Test
from rest_framework import permissions, viewsets


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all().order_by("id")
