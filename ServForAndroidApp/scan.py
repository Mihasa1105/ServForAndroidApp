import cv2
import numpy as np

# Загружаем изображение
widthImg = 800
heightImg = 1000

image = cv2.imread('test3.png')
imgBlank = np.zeros((heightImg,widthImg, 3), np.uint8)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 1)
# adaptive_thresh = cv2.adaptiveThreshold(
#     blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#     cv2.THRESH_BINARY_INV, 11, 2
# )
adaptive_thresh = cv2.Canny(blurred, 70, 160)
kernel = np.ones((5, 5))
dial = cv2.dilate(adaptive_thresh, kernel, iterations=2)
adaptive_thresh = cv2.erode(dial, kernel, iterations=1)

imgContours = image.copy()
imgBigContour = image.copy()

contours, hierarchy = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)



def reorder(myPoints):

    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] =myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]

    return myPointsNew


def drawRectangle(img,biggest,thickness):
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)

    return img


biggest = np.array([])
max_area = 0
for i in contours:
    area = cv2.contourArea(i)
    if area > 5000:
        peri = cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, 0.02 * peri, True)
        if area > max_area and len(approx) == 4:
            biggest = approx
            max_area = area

if biggest.size != 0:
    biggest = reorder(biggest)
    cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)
    imgBigContour = drawRectangle(imgBigContour, biggest, 2)
    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarpColored = cv2.warpPerspective(image, matrix, (widthImg, heightImg))

    imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
    imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))

    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
    imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
    imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)

#     imageArray = ([image, gray, adaptive_thresh, imgContours],
#                   [imgBigContour, imgWarpColored, imgWarpGray, imgAdaptiveThre])
#
# else:
#     imageArray = ([image,gray,adaptive_thresh,imgContours],
#                     [imgBlank, imgBlank, imgBlank, imgBlank])


cv2.imshow("Adaptive Threshold", imgAdaptiveThre)  # Отображаем адаптивный порог
cv2.waitKey(0)

# # Применяем морфологическое закрытие для устранения мелких разрывов в контуре
#
# kernel = np.ones((5, 5), np.uint8)
# closed = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
# cv2.imshow("Morphological Closing", closed)  # Отображаем результат морфологического закрытия
# cv2.waitKey(0)
#
# # Поиск контуров после морфологических преобразований
# contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
# # Инициализируем переменные для поиска контуров
# sheet_contour = None
# max_area = 0
#
# # Ищем контур, который является приблизительно прямоугольным
# for contour in contours:
#     area = cv2.contourArea(contour)
#     if area > max_area:
#         # Проверяем, является ли контур приблизительно прямоугольным
#         approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
#         if len(approx) == 4:  # Контур имеет 4 угла
#             sheet_contour = approx
#             max_area = area
#
# # Проверяем, что нашли контур листа
# if sheet_contour is not None:
#     # Рисуем найденный контур листа на изображении
#     cv2.drawContours(image, [sheet_contour], -1, (0, 255, 0), 2)  # Рисуем контур листа зеленым цветом
#     cv2.imshow("Detected Sheet Contour", image)  # Отображаем изображение с контуром листа
#     cv2.waitKey(0)
#
#     # Создаем маску, чтобы ограничить область поиска внутри листа
#     mask = np.zeros_like(gray)
#     cv2.drawContours(mask, [sheet_contour], -1, 255, thickness=cv2.FILLED)
#     sheet_area = cv2.bitwise_and(closed, closed, mask=mask)
#
#     # Отображаем область листа
#     cv2.imshow("Sheet Area", sheet_area)
#     cv2.waitKey(0)
#
#     # Поиск контуров внутри области листа для выявления маркеров
#     contours, _ = cv2.findContours(sheet_area, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     # Параметры для обнаружения углов
#     corners = []
#
#     # Ищем квадратные маркеры внутри области листа
#     for contour in contours:
#         # Проверяем, похож ли контур на квадратный маркер
#         approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
#         x, y, w, h = cv2.boundingRect(approx)
#
#         if len(approx) == 4 and w >= 20 and h >= 20:
#             # Определяем центр маркера
#             center_x, center_y = x + w // 2, y + h // 2
#             corners.append((center_x, center_y))
#
#     # Отображаем угловые маркеры
#     for corner in corners:
#         cv2.circle(image, corner, 10, (0, 0, 255), -1)
#     cv2.imshow("Detected Corners on Sheet", image)
#     cv2.waitKey(0)
#
#     # Проверяем, что нашли все 4 угла, и продолжаем выравнивание
#     if len(corners) == 4:
#         corners = sorted(corners, key=lambda x: (x[1], x[0]))
#         if corners[0][0] > corners[1][0]:
#             corners[0], corners[1] = corners[1], corners[0]
#         if corners[2][0] < corners[3][0]:
#             corners[2], corners[3] = corners[3], corners[2]
#
#         width, height = 800, 1000
#         dst_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
#         src_points = np.float32(corners)
#
#         matrix = cv2.getPerspectiveTransform(src_points, dst_points)
#         aligned_image = cv2.warpPerspective(image, matrix, (width, height))
#
#         # Отображаем выровненное изображение
#         cv2.imshow("Aligned Image", aligned_image)
#         cv2.waitKey(0)
#     else:
#         print("Не удалось обнаружить все четыре угловых маркера.")
# else:
#     print("Не удалось определить контур листа.")
#
# cv2.destroyAllWindows()
