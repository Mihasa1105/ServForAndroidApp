
from .models import Test, TestResults, TestImage
from rest_framework import viewsets
from .serializers import TestImageSerializer, TestResultsSerializer, TestSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .scan import scan
import cv2
import numpy as np
from PIL import Image
import io
from rest_framework.decorators import action
from rest_framework.response import Response
import base64

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    @action(detail=False, methods=['get'], url_path='teacher_tests')
    def get_teacher_tests(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if teacher_id is not None:
            tests = Test.objects.filter(user_id=teacher_id).values('id', 'test_name', 'subject_id__subject_name')
            return Response(tests)
        return Response({"error": "teacher_id parameter is required"}, status=400)


class TestResultsViewSet(viewsets.ModelViewSet):
    queryset = TestResults.objects.all()
    serializer_class = TestResultsSerializer


class TestImageViewSet(viewsets.ModelViewSet):
    queryset = TestImage.objects.all()
    serializer_class = TestImageSerializer

    def create(self, request, *args, **kwargs):
        # Получение изображения и ID теста из запроса
        image_file = request.FILES.get("image")
        test_id = request.data.get("test_id")
        if not test_id:
            return Response({"error": "test_id is required"}, status=400)

        # Открытие изображения
        image = Image.open(image_file).convert("RGB")
        open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Обработка изображения
        processed_image, student_answers, correct_count = scan(open_cv_image, test_id)

        if student_answers is None:
            return Response({"error": "Failed to process the image"}, status=400)

        # Формирование ответа с изображением
        pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
        byte_io = io.BytesIO()
        pil_image.save(byte_io, 'JPEG')
        byte_io.seek(0)
        image_base64 = base64.b64encode(byte_io.read()).decode('utf-8')  # Кодирование в base64

        response_data = {
            "image": image_base64,  # Возвращаем строку base64
            "student_answers": student_answers,
            "correct_count": correct_count,
        }

        return Response(response_data, content_type="application/json")