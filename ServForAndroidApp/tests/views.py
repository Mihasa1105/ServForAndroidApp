
from .models import Test, TestResults, TestImage
from rest_framework import viewsets
from .serializers import TestImageSerializer, TestResultsSerializer, TestSerializer
from .scan import scan
import cv2
import numpy as np
from PIL import Image
import io
from rest_framework.decorators import action
from rest_framework.response import Response
from .management.commands.telegram_bot import send_test_result
import base64
import json
import asyncio

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

    def create(self, request, *args, **kwargs):
        test_id = request.data.get("test_id")
        student_id = request.data.get("student_id")
        answers_raw = request.data.get("answers", "{}")  # Гарантируем, что значение есть
        image = request.data.get("image", None)

        if not test_id or not student_id:
            return Response({"detail": "Missing required fields"}, status=400)

        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found"}, status=404)

        # Проверяем, нужно ли парсить строки в JSON
        if isinstance(answers_raw, str):
            try:
                student_answers = json.loads(answers_raw)  # Преобразуем строку в словарь
            except json.JSONDecodeError:
                return Response({"detail": "Invalid JSON format in answers"}, status=400)
        else:
            student_answers = answers_raw  # Уже JSON-объект

        correct_answers = test.answers  # JSON с правильными ответами
        total_points = 0
        max_points = 0

        for question, correct_data in correct_answers.items():
            if question in student_answers:
                student_response = student_answers[question]
                correct_options = {k: v for k, v in correct_data.items() if k != "pt"}  # Убираем pt
                pt = int(correct_data.get("pt", 0))  # Баллы за вопрос
                max_points += pt  # Общие возможные баллы

                if student_response == correct_options:
                    total_points += pt  # Добавляем баллы, если ответ полностью совпадает

        # Подсчёт процента и отметки
        percentage = (total_points / max_points) * 100 if max_points > 0 else 0
        mark = round(percentage / 10)  # Округляем и ставим отметку от 1 до 10
        mark = max(1, min(mark, 10))  # Ограничиваем диапазон от 1 до 10

        # Сохранение результата
        test_result = TestResults.objects.create(
            test_id=test,
            student_id_id=student_id,
            answers=student_answers,
            image=image,
            points=total_points,
            mark=mark
        )

        student = test_result.student_id
        if student.connect_address:
            asyncio.run(send_test_result(test.test_name, student.connect_address, total_points, mark, image))

        serializer = self.get_serializer(test_result)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'], url_path='results_by_test')
    def get_results_by_test(self, request):
        test_id = request.query_params.get('test_id', None)
        if test_id is None:
            return Response({"detail": "Test ID is required"}, status=400)

        # Фильтруем результаты по ID теста
        results = TestResults.objects.filter(test_id=test_id)
        result_data = []

        for result in results:
            correct_answers_count = result.points
            mark = result.mark

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
                "correct_answers_count": correct_answers_count,
                "mark": mark
            })

        return Response(result_data)



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
        processed_image, student_answers, total_points, grade = scan(open_cv_image, test_id)

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
            "total_points": total_points,
            "grade": grade,
        }

        return Response(response_data, content_type="application/json")