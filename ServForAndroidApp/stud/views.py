
from .models import Subjects, Students, Group, UserSubject
from rest_framework import viewsets
from .serializers import SubjectSerializer, StudSerializer, GroupSerializer, UserSubjectSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subjects.objects.all()
    serializer_class = SubjectSerializer

class UserSubjectViewSet(viewsets.ViewSet):
    queryset = UserSubject.objects.all()
    serializer_class = UserSubjectSerializer
    @action(detail=False, methods=['get'], url_path='get_subjects_by_teacher')
    def get_subjects_by_teacher(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if teacher_id is not None:
            subjects = UserSubject.objects.filter(teacher_id=teacher_id).select_related('subject_id')
            subject_data = {subj.subject_id.id: subj.subject_id.subject_name for subj in subjects}
            return Response(subject_data)
        return Response({"error": "teacher_id parameter is required"}, status=400)


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

