
from .models import Subjects, Students, Group
from rest_framework import viewsets
from .serializers import SubjectSerializer, StudSerializer, GroupSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subjects.objects.all()
    serializer_class = SubjectSerializer


class StudViewSet(viewsets.ModelViewSet):
    queryset = Students.objects.all()
    serializer_class = StudSerializer

    @action(detail=False, methods=['get'], url_path='get_stud_by_gr')
    def get_teacher_tests(self, request):
        group_id = request.query_params.get('group_id')
        if group_id is not None:
            studs = Students.objects.filter(group_id=group_id).annotate(
                initials=Concat(
                    F('surname'), Value(' '),
                    F('name')[0], Value('.'),
                    F('father_name')[0], Value('.'),
                    output_field=CharField()
                )
            ).values('id', 'initials')
            return Response(studs)
        return Response({"error": "group_id parameter is required"}, status=400)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

