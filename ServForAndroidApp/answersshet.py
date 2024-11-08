import cv2
import numpy as np

# Загрузка четырёх разных угловых меток
marker_bl = cv2.imread("markers/bottom_left.png", cv2.IMREAD_GRAYSCALE)
marker_br = cv2.imread("markers/bottom_right.png", cv2.IMREAD_GRAYSCALE)
marker_tl = cv2.imread("markers/top_left.png", cv2.IMREAD_GRAYSCALE)
marker_tr = cv2.imread("markers/top_right.png", cv2.IMREAD_GRAYSCALE)

# Размер меток (предполагаем, что все метки одинакового размера)
marker_size = marker_tl.shape[0]

# Настройки для листа
width, height = 1240, 1754  # Размер A4 в пикселях при разрешении 150 DPI
columns = ['A', 'B', 'C', 'D', 'E']  # Варианты ответов
num_questions = 50  # Количество вопросов
questions_per_column = 25  # Вопросы в одной колонке
circle_radius = 15  # Радиус кружков для ответов
circle_spacing_y = 45  # Вертикальный интервал между вопросами
margin_top = 200  # Увеличен отступ сверху, чтобы разместить метки
margin_left = 200  # Отступ слева для первой колонки
column_spacing_x = 50  # Горизонтальный интервал между колонками с вариантами

# Создаём белый фон для листа
answer_sheet = np.ones((height, width), dtype=np.uint8) * 255

# Размещение четырёх разных меток в углах
answer_sheet[50:50 + marker_size, 50:50 + marker_size] = marker_tl  # Верхний левый
answer_sheet[50:50 + marker_size, width - 50 - marker_size:width - 50] = marker_tr  # Верхний правый
answer_sheet[height - 50 - marker_size:height - 50, 50:50 + marker_size] = marker_bl  # Нижний левый
answer_sheet[height - 50 - marker_size:height - 50, width - 50 - marker_size:width - 50] = marker_br  # Нижний правый

# Определение позиций для столбцов с вариантами и добавление букв (A, B, C, D) над каждым
start_x = margin_left

for i, column in enumerate(columns):
    cv2.putText(
        answer_sheet, column,
        (start_x + i * column_spacing_x - 5, margin_top - 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2
    )

# Рисуем вопросы с вариантами ответов
for q in range(num_questions):
    question_num = q + 1
    row = q % questions_per_column
    col = q // questions_per_column

    # Позиция для номера вопроса
    question_y = margin_top + row * circle_spacing_y
    question_x = margin_left + col * (4 * column_spacing_x + 100)

    # Рисуем номер вопроса
    cv2.putText(
        answer_sheet, f"{question_num:02d}",
        (question_x - 60, question_y + 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
    )

    # Рисуем кружки для вариантов ответа (A, B, C, D)
    for option in range(5):
        circle_x = question_x + option * column_spacing_x
        cv2.circle(answer_sheet, (circle_x, question_y), circle_radius, (0, 0, 0), 2)

# Сохраняем изображение
cv2.imwrite("generated_answer_sheet_with_different_markers.png", answer_sheet)

# Показываем изображение
cv2.imshow("Answer Sheet with Different Markers", answer_sheet)
cv2.waitKey(0)
cv2.destroyAllWindows()
