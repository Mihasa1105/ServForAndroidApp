import cv2
import numpy as np

# Параметры для макета
width, height = 800, 1000  # Размер холста
column_x_offsets = [200, 500]  # Отступы по X для двух столбцов
y_start = 200  # Начальная позиция Y
y_gap = 60  # Расстояние между вопросами

# Создаем белый холст
canvas = np.ones((height, width, 3), dtype="uint8") * 255

# Шрифт и параметры
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_thickness = 1

# Добавляем заголовок вариантов (заменим на английские буквы A, B, C, D)
for x_offset in column_x_offsets:
    for i, letter in enumerate(['A', 'B', 'C', 'D']):
        # Пробуем отрисовать текст выше кружков
        cv2.putText(canvas, letter, (x_offset + i * 40 + 15, y_start - 25), font, font_scale, (0, 0, 0), font_thickness)

# Добавляем вопросы и кружки ответов
question_number = 1
for column in column_x_offsets:
    y_position = y_start
    for _ in range(10):
        # Сдвигаем номер вопроса вниз для центровки
        cv2.putText(canvas, str(question_number), (column - 40, y_position + 10), font, font_scale, (0, 0, 0),
                    font_thickness)

        # Рисуем кружки для ответов
        for i in range(4):
            circle_x = column + i * 40 + 25
            circle_y = y_position
            cv2.circle(canvas, (circle_x, circle_y), 10, (0, 0, 0), 1)

        # Переходим к следующему вопросу
        question_number += 1
        y_position += y_gap

# Добавляем угловые метки для распознавания
corner_size = 20
cv2.rectangle(canvas, (0, 0), (corner_size, corner_size), (0, 0, 0), -1)  # Верхний левый
cv2.rectangle(canvas, (width - corner_size, 0), (width, corner_size), (0, 0, 0), -1)  # Верхний правый
cv2.rectangle(canvas, (0, height - corner_size), (corner_size, height), (0, 0, 0), -1)  # Нижний левый
cv2.rectangle(canvas, (width - corner_size, height - corner_size), (width, height), (0, 0, 0), -1)  # Нижний правый

# Сохраняем изображение
cv2.imwrite('answer_sheet_template.png', canvas)
cv2.imshow('Answer Sheet Template', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
