import json

import cv2
import numpy as np
import os
from django.shortcuts import get_object_or_404
from .models import Test
from PIL import Image
import pdb

epsilon = 10 #image error sensitivity
test_sensitivity_epsilon = 7.5 #bubble darkness error sensitivity
answer_choices = ['A', 'B', 'C', 'D', 'E', '?'] #answer choices

scaling = [1240.0, 1754.0]  # Масштаб для A4 8.5x11 дюймов
columns = [[120.0 / scaling[0], 50.0 / scaling[1]], [630.0 / scaling[0], 50.0 / scaling[1]]]  # Столбцы для ответов
radius = 14.5 / scaling[0]  # Радиус кружков
spacing = [55.0 / scaling[0], 49 / scaling[1]]  # Интервалы для ответов
margin_up = 70.0 / scaling[1]


def get_correct_answers(test_id):
    test = get_object_or_404(Test, id=test_id)
    return test.answers, test.question_quantity

def ProcessPage(paper, test_id):

    answers = [] #contains answers
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) #convert image to grayscale
    corners = FindCorners(paper) #find the corners of the bubbled area
    print("Corners detected:", corners)
    if corners is None:
        return [], paper, 0, 0

    for corner in corners:
        cv2.rectangle(paper, (corner[0], corner[1]), (corner[0], corner[1]), (0, 255, 0), thickness=2)


    dimensions = [corners[1][0] - corners[0][0], corners[2][1] - corners[0][1]]

    correct_answers, question_quantity= get_correct_answers(test_id) #Получаем правильные ответы

    # Ожидаемое количество вопросов
    processed_questions = 0
    student_answers = {
        i + 1: {
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
            "E": 0
        }
        for i in range(question_quantity)
    }
    total_points = 0  # Общая сумма баллов
    total_max_points = 0  # Максимально возможная сумма баллов

    for k in range(0, 2):  # два столбца
        for i in range(0, 25):  # кол-во вопросов (всего должно быть 10, например)
            if processed_questions >= question_quantity:
                break
            question_answer = correct_answers[str(processed_questions+1)]

            is_correct = 1
            questions = []
            coordinates = []

            for j in range(0, 5):  # варианты ответа A, B, C, D, E
                # координаты пузырька для ответа
                x1 = int((columns[k][0] + j * spacing[0] - radius * 1.5) * dimensions[0] + corners[0][0])
                y1 = int((columns[k][1] + i * spacing[1] - radius + margin_up) * dimensions[1] + corners[0][1])
                x2 = int((columns[k][0] + j * spacing[0] + radius * 1.5) * dimensions[0] + corners[0][0])
                y2 = int((columns[k][1] + i * spacing[1] + radius + margin_up) * dimensions[1] + corners[0][1])
                questions.append(gray_paper[y1:y2, x1:x2]) # Записываем область бумаги
                coordinates.append((x1, y1, x2, y2)) # Записываем координаты

            means = [np.mean(question) for question in questions]
            threshold = min(means) + test_sensitivity_epsilon # Яркость для сравнения

            is_correct = True # Правильно ли ответили на вопрос

            for j in range(0, 5): # Перебираем все 5 кружочков
                if means[j] < threshold: # Если кружочек предположительно ответ
                    student_answers[processed_questions + 1][answer_choices[j]] = 1
                    if question_answer[answer_choices[j]] == '1':
                        x1, y1, x2, y2 = coordinates[j]
                        cv2.rectangle(paper, (x1, y1), (x2, y2), (0, 255, 0), thickness=3)
                    else:
                        x1, y1, x2, y2 = coordinates[j]
                        cv2.rectangle(paper, (x1, y1), (x2, y2), (0, 0, 255), thickness=3)
                        is_correct = False
                else:
                    student_answers[processed_questions + 1][answer_choices[j]] = 0
                    if question_answer[answer_choices[j]] == '0':
                        x1, y1, x2, y2 = coordinates[j]
                        cv2.rectangle(paper, (x1, y1), (x2, y2), (0, 255, 0), thickness=3)
                    else:
                        x1, y1, x2, y2 = coordinates[j]
                        cv2.rectangle(paper, (x1, y1), (x2, y2), (0, 0, 255), thickness=3)
                        is_correct = False

            points = int(question_answer['pt'])
            total_max_points += points

            final_x = int(x2 + spacing[0])
            final_y = int(y1 + (y2 - y1) / 2)

            if is_correct:
                total_points += points
                cv2.putText(paper, 'V', (final_x, final_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                            2)  # Зеленая галочка
            else:
                cv2.putText(paper, 'X', (final_x, final_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                            2)  # Красный крестик

            processed_questions += 1

        score_percentage = (total_points / total_max_points) * 100 if total_max_points else 0

        # Округление процента до оценки от 1 до 10
        grade = round(score_percentage / 10)  # Переводим в оценку от 1 до 10

        # Возвращаем изменённое изображение, JSON с ответами, количество баллов и оценку
        return student_answers, paper, total_points, grade


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Формируем путь к маркерам
MARKERS_DIR = os.path.join(BASE_DIR, 'tests', 'markers')

# Загружаем маркеры
marker_tl = cv2.imread(os.path.join(MARKERS_DIR, 'top_left.png'), cv2.IMREAD_GRAYSCALE)
marker_tr = cv2.imread(os.path.join(MARKERS_DIR, 'top_right.png'), cv2.IMREAD_GRAYSCALE)
marker_bl = cv2.imread(os.path.join(MARKERS_DIR, 'bottom_left.png'), cv2.IMREAD_GRAYSCALE)
marker_br = cv2.imread(os.path.join(MARKERS_DIR, 'bottom_right.png'), cv2.IMREAD_GRAYSCALE)

template_matching_threshold = 0.6

def FindCorners(paper):
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY)

    # Определяем ratio для масштабирования меток под размер изображения
    ratio = len(paper[0]) / 1240.0  # 1240 - ширина листа A4 при 150 DPI

    # Масштабируем метки под изображение
    markers = [
        cv2.resize(marker_tl, (0, 0), fx=ratio, fy=ratio),
        cv2.resize(marker_tr, (0, 0), fx=ratio, fy=ratio),
        cv2.resize(marker_bl, (0, 0), fx=ratio, fy=ratio),
        cv2.resize(marker_br, (0, 0), fx=ratio, fy=ratio),
    ]

    # Позиции углов на листе, где будут искать каждую метку
    search_regions = [
        (0, len(paper[0]) // 2, 0, len(paper) // 2),  # top-left
        (len(paper[0]) // 2, len(paper[0]), 0, len(paper) // 2),  # top-right
        (0, len(paper[0]) // 2, len(paper) // 2, len(paper)),  # bottom-left
        (len(paper[0]) // 2, len(paper[0]), len(paper) // 2, len(paper)),  # bottom-right
    ]

    corners = []

    for i, marker in enumerate(markers):
        x_start, x_end, y_start, y_end = search_regions[i]
        region = gray_paper[y_start:y_end, x_start:x_end]

        # Шаблонное сопоставление
        res = cv2.matchTemplate(region, marker, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= template_matching_threshold:
            # Найденное положение угла с учетом смещения для региона
            corner_x = max_loc[0] + x_start
            corner_y = max_loc[1] + y_start
            corners.append((corner_x + marker.shape[1], corner_y + marker.shape[0]))

            # Отметим найденный угол на изображении
            cv2.rectangle(paper, (corner_x, corner_y),
                          (corner_x + marker.shape[1], corner_y + marker.shape[0]),
                          (0, 255, 0), 2)

        else:
            print(f"Метка {i + 1} не найдена с достаточной точностью")

    # Если найдено меньше четырех углов, возвращаем None
    if len(corners) < 4:
        print("Не удалось найти все четыре угла.")
        return None

    return corners