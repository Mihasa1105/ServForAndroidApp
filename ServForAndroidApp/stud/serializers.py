from rest_framework import serializers
from .models import Subjects, Students, Group, UserSubject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = '__all__'

class StudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UserSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubject
        fields = '__all__'