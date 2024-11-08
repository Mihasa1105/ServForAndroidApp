import cv2
import numpy as np
from process_page import ProcessPage

def clockwise_sort(x):
	return (np.arctan2(x[0] - mx, x[1] - my) + 0.02 * np.pi) % (2*np.pi)


image = cv2.imread("test19.png")
ratio = len(image[0]) / 500.0
original_image = image.copy()

image = cv2.resize(image, (0,0), fx=1/ratio, fy=1/ratio)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)
edged = cv2.Canny(gray, 200, 200)

contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
biggestContour = None

for contour in contours:
	peri = cv2.arcLength(contour, True)
	approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

	if len(approx) == 4:
		biggestContour = approx
		break

points = []
desired_points = [[0, 1754], [0, 0], [1240, 0], [1240, 1754]]
desired_points = np.float32(desired_points)

if biggestContour is not None:
	for i in range(0, 4):
		points.append(biggestContour[i][0])

mx = sum(point[0] for point in points) / 4
my = sum(point[1] for point in points) / 4

points.sort(key=clockwise_sort, reverse=True)
points = np.float32(points)

paper = []
points *= ratio
answers = 1
if biggestContour is not None:
	M = cv2.getPerspectiveTransform(points, desired_points)
	paper = cv2.warpPerspective(original_image, M, (1240, 1754))
	answers, paper = ProcessPage(paper)
	cv2.imshow("Scanned Paper", cv2.resize(paper, (0, 0), fx=0.7, fy=0.7))

if biggestContour is not None:
	if answers != -1:
		cv2.drawContours(image, [biggestContour], -1, (0, 255, 0), 3)
		# print answers
		# if codes is not None:
		# 	print codes
	else:
		cv2.drawContours(image, [biggestContour], -1, (0, 0, 255), 3)

cv2.imshow("Original Image", cv2.resize(image, (0, 0), fx=0.7, fy=0.7))

cv2.waitKey(0)