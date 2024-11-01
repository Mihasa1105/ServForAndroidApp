from rest_framework import serializers
from .models import Test, TestResults, TestImage


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class TestResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResults
        fields = '__all__'


class TestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestImage
        fields = '__all__'
