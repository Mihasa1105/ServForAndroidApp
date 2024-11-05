import cv2
import numpy as np

# Загружаем изображение
widthImg = 800
heightImg = 1000

image = cv2.imread('test14.png')
imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 1)
adaptive_thresh = cv2.Canny(blurred, 50, 200)

kernel = np.ones((5, 5))
dial = cv2.dilate(adaptive_thresh, kernel, iterations=2)
adaptive_thresh = cv2.erode(dial, kernel, iterations=1)

imgContours = image.copy()
imgBigContour = image.copy()

contours, hierarchy = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)
imgcopy = cv2.resize(imgContours, (600, 750))
cv2.imshow('origin', imgcopy)
cv2.waitKey(0)


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

        img_contours = np.uint8(np.zeros((image.shape[0], image.shape[1])))
        cv2.drawContours(img_contours, [approx], -1, (255, 255, 255), 1)
        imgcopy = cv2.resize(img_contours, (600, 750))
        cv2.imshow('origin', imgcopy)
        cv2.waitKey(0)

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

imgcopy = cv2.resize(imgAdaptiveThre, (600, 750))
cv2.imshow('origin', imgcopy)
cv2.waitKey(0)

cut_img_gray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
cut_img_blurred = cv2.GaussianBlur(cut_img_gray, (5, 5), 0)
cut_img_thresh = cv2.Canny(cut_img_blurred, 40, 200)

imgcopy = cv2.resize(cut_img_thresh, (600, 750))
cv2.imshow('origin', imgcopy)
cv2.waitKey(0)

cut_img_kernel = np.ones((5, 5))
cut_img_dial = cv2.dilate(cut_img_thresh, cut_img_kernel, iterations=2)
cut_img_thresh = cv2.erode(cut_img_dial, cut_img_kernel, iterations=1)

imgcopy = cv2.resize(cut_img_thresh, (600, 750))
cv2.imshow('origin', imgcopy)
cv2.waitKey(0)

cut_img_contours, cut_img_hierarchy = cv2.findContours(cut_img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

min_radius = 10
max_radius = 20

filled_circles = []

for cnt in cut_img_contours:
    # Проверить, является ли контур достаточно круглым
    (x, y), radius = cv2.minEnclosingCircle(cnt)
    if min_radius < radius < max_radius:
        # Выделить кружок и проверить его заполненность
        mask = np.zeros(cut_img_thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [cnt], -1, 255, -1)

        # Подсчитать количество черных пикселей внутри круга
        circle_region = cv2.bitwise_and(cut_img_thresh, cut_img_thresh, mask=mask)
        filled_ratio = cv2.countNonZero(circle_region) / (np.pi * radius ** 2)

        # Если заполненность выше порога, считать круг заполненным
        if filled_ratio > 0.5:  # порог можно подстроить
            filled_circles.append((int(x), int(y)))

print("Заполненные кружки:", filled_circles)