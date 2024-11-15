from rest_framework import serializers
from .models import User, UserCode



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCode
        fields = '__all__'
