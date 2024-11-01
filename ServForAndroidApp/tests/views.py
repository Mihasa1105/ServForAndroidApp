from django.shortcuts import render

from .models import Test, TestResults
from rest_framework import viewsets
from .serializers import TestSerializer, TestResultsSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class TestResultsViewSet(viewsets.ModelViewSet):
    queryset = TestResults.objects.all()
    serializer_class = TestResultsSerializer
