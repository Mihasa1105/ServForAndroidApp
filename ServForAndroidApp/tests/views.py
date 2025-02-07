
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
        subject_id = request.query_params.get('subject_id')

        if teacher_id is None:
            return Response({"error": "teacher_id parameter is required"}, status=400)

        # Базовая фильтрация по teacher_id
        filters = {'user_id': teacher_id}

        # Добавляем фильтр по subject_id, если он передан
        if subject_id is not None:
            filters['subject_id'] = subject_id

        tests = Test.objects.filter(**filters).values('id', 'test_name', 'question_quantity')
        return Response(tests)


class TestResultsViewSet(viewsets.ModelViewSet):
    queryset = TestResults.objects.all()
    serializer_class = TestResultsSerializer

    @action(detail=False, methods=['get'], url_path='results_by_test')
    def get_results_by_test(self, request):
        test_id = request.query_params.get('test_id', None)
        if test_id is None:
            return Response({"detail": "Test ID is required"}, status=400)

        # Фильтруем результаты по ID теста
        results = TestResults.objects.filter(test_id=test_id)
        result_data = []

        for result in results:
            # Сравниваем ответы
            correct_answers_count = self.calculate_correct_answers(result)

            # Получаем данные студента
            student = result.student_id
            student_name = f"{student.surname} {student.name[0]}. {student.father_name[0]}."

            # Получаем название группы (без повторного запроса в базу данных)
            group_name = student.group_id.group_name

            # Добавляем результат в список
            result_data.append({
                "result_id": result.id,
                "student_name": student_name,
                "group_name": group_name,
                "correct_answers_count": correct_answers_count
            })

        return Response(result_data)


    def calculate_correct_answers(self, result):
        correct_answers_count = 0
        test_answers = result.test_id.answers  # Ответы на тест
        student_answers = result.answers  # Ответы студента

        # Сравниваем ответы
        for question, answer in student_answers.items():
            if test_answers.get(question) == answer:
                correct_answers_count += 1
        return correct_answers_count


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