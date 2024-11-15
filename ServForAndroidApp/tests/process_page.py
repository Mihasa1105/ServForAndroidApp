import cv2
import numpy as np
from PIL import Image

epsilon = 10 #image error sensitivity
test_sensitivity_epsilon = 5 #bubble darkness error sensitivity
answer_choices = ['A', 'B', 'C', 'D', 'E', '?'] #answer choices

scaling = [1240.0, 1754.0]  # Масштаб для A4 8.5x11 дюймов
columns = [[120.0 / scaling[0], 50.0 / scaling[1]], [630.0 / scaling[0], 50.0 / scaling[1]]]  # Столбцы для ответов
radius = 14.5 / scaling[0]  # Радиус кружков
spacing = [55.0 / scaling[0], 49 / scaling[1]]  # Интервалы для ответов
margin_up = 60.0 / scaling[1]


def ProcessPage(paper):

    answers = [] #contains answers
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) #convert image to grayscale
    corners = FindCorners(paper) #find the corners of the bubbled area
    print("Corners detected:", corners)
    if corners is None:
        return [-1], paper, [-1]

    for corner in corners:
        cv2.rectangle(paper, (corner[0], corner[1]), (corner[0], corner[1]), (0, 255, 0), thickness=2)


    dimensions = [corners[1][0] - corners[0][0], corners[2][1] - corners[0][1]]

    for k in range(0, 2):  # columns
        for i in range(0, 25):  # rows
            questions = []
            for j in range(0, 5):  # answers
                # coordinates of the answer bubble
                x1 = int((columns[k][0] + j * spacing[0] - radius * 1.5) * dimensions[0] + corners[0][0])
                y1 = int((columns[k][1] + i * spacing[1] - radius + margin_up) * dimensions[1] + corners[0][1])
                x2 = int((columns[k][0] + j * spacing[0] + radius * 1.5) * dimensions[0] + corners[0][0])
                y2 = int((columns[k][1] + i * spacing[1] + radius + margin_up) * dimensions[1] + corners[0][1])

                # draw rectangles around bubbles
                cv2.rectangle(paper, (x1, y1), (x2, y2), (255, 0, 0), thickness=1, lineType=8, shift=0)

                # crop answer bubble
                questions.append(gray_paper[y1:y2, x1:x2])

            means = []
            x1 = int((columns[k][0] - radius*8)*dimensions[0] + corners[0][0])
            y1 = int((columns[k][1] + i*spacing[1] + margin_up + 0.5*radius)*dimensions[1] + corners[0][1])

            for question in questions:
                means.append(np.mean(question))
            min_arg = np.argmin(means)
            min_val = means[min_arg]
            means[min_arg] = 255
            min_val2 = means[np.argmin(means)]
            if min_val2 - min_val < test_sensitivity_epsilon:
                #if so, then the question has been double bubbled and is invalid
                min_arg = 5

            #write the answer
            cv2.putText(paper, answer_choices[min_arg], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 150, 0), 2)

            #append the answers to the array
            answers.append(answer_choices[min_arg])

    return answers, paper


marker_tl = cv2.imread("tests/markers/top_left.png", cv2.IMREAD_GRAYSCALE)
marker_tr = cv2.imread("tests/markers/top_right.png", cv2.IMREAD_GRAYSCALE)
marker_bl = cv2.imread("tests/markers/bottom_left.png", cv2.IMREAD_GRAYSCALE)
marker_br = cv2.imread("tests/markers/bottom_right.png", cv2.IMREAD_GRAYSCALE)

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