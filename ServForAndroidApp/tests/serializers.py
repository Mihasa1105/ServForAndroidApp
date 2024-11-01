from rest_framework import serializers
from .models import Test, TestResults


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class TestResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResults
        fields = '__all__'
