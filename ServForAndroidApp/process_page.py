import cv2
import numpy as np
from PIL import Image

epsilon = 10 #image error sensitivity
test_sensitivity_epsilon = 10 #bubble darkness error sensitivity
answer_choices = ['A', 'B', 'C', 'D', 'E', '?'] #answer choices

tags = [cv2.imread("markers/top_left.png", cv2.IMREAD_GRAYSCALE),
        cv2.imread("markers/top_right.png", cv2.IMREAD_GRAYSCALE),
        cv2.imread("markers/bottom_left.png", cv2.IMREAD_GRAYSCALE),
        cv2.imread("markers/bottom_right.png", cv2.IMREAD_GRAYSCALE)]

scaling = [1240.0, 1754.0] #scaling factor for 8.5in. x 11in. paper
columns = [[200.0 / scaling[0], 50.0 / scaling[1]], [800.0 / scaling[0], 50.0 / scaling[1]]]  # Примерные значения для двух столбцов
radius = 15.0 / scaling[0]  # Примерное значение, если радиус - 15 пикселей
spacing = [50.0 / scaling[0], 45.0 / scaling[1]]  # Примерное значение для вертикального и горизонтального интервала


def ProcessPage(paper):

    cv2.imshow("Original Image", cv2.resize(paper, (0, 0), fx=0.5   , fy=0.5))

    cv2.waitKey(0)

    answers = [] #contains answers
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) #convert image to grayscale
    corners = FindCorners(paper) #find the corners of the bubbled area
    print("Corners detected:", corners)
    if corners is None:
        return [-1], paper, [-1]

    for corner in corners:
        cv2.rectangle(
            paper,
            (corner[0] - 10, corner[1] - 10),
            (corner[0] + 10, corner[1] + 10),
            (0, 255, 0),
            thickness=2
        )

        # Показать изображение с найденными углами
    cv2.imshow("Corners Detected", cv2.resize(paper, (0, 0), fx=0.5, fy=0.5))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    dimensions = [corners[1][0] - corners[0][0], corners[2][1] - corners[0][1]]

    for k in range(0, 2):  # columns
        for i in range(0, 25):  # rows
            questions = []
            for j in range(0, 5):  # answers
                # coordinates of the answer bubble
                x1 = int((columns[k][0] + j * spacing[0] - radius * 1.5) * dimensions[0] + corners[0][0])
                y1 = int((columns[k][1] + i * spacing[1] - radius) * dimensions[1] + corners[0][1])
                x2 = int((columns[k][0] + j * spacing[0] + radius * 1.5) * dimensions[0] + corners[0][0])
                y2 = int((columns[k][1] + i * spacing[1] + radius) * dimensions[1] + corners[0][1])

                # draw rectangles around bubbles
                cv2.rectangle(paper, (x1, y1), (x2, y2), (255, 0, 0), thickness=1, lineType=8, shift=0)

                # crop answer bubble
                questions.append(gray_paper[y1:y2, x1:x2])

            means = []
            x1 = int((columns[k][0] - radius*8)*dimensions[0] + corners[0][0])
            y1 = int((columns[k][1] + i*spacing[1] + 0.5*radius)*dimensions[1] + corners[0][1])

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
            cv2.putText(paper, answer_choices[min_arg], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 150, 0), 1)

            #append the answers to the array
            answers.append(answer_choices[min_arg])

    return answers, paper


def FindCorners(paper):
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) #convert image of paper to grayscale

    #scaling factor used later
    ratio = len(paper[0]) / 500.0

    #error detection
    if ratio == 0:
        return -1

    corners = [] #array to hold found corners

    #try to find the tags via convolving the image
    for tag in tags:
        # tag = cv2.resize(tag, (0,0), fx=1/ratio, fy=1/ratio) #resize tags to the ratio of the image



        #convolve the image
        convimg = (cv2.filter2D(np.float32(cv2.bitwise_not(gray_paper)), -1, np.float32(cv2.bitwise_not(tag))))

        #find the maximum of the convolution
        corner = np.unravel_index(convimg.argmax(), convimg.shape)

        #append the coordinates of the corner
        corners.append([corner[1], corner[0]]) #reversed because array order is different than image coordinate
        test = paper.copy()
        cv2.rectangle(test, (corner[0] - 10, corner[1] - 10),
                      (corner[0] + 10, corner[1] + 10), (0, 255, 0), thickness=2, lineType=8,
                      shift=0)

        cv2.imshow("Corners Sycle Detected", cv2.resize(test, (0, 0), fx=0.5, fy=0.5))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    test = paper.copy()

    #draw the rectangle around the detected markers
    for corner in corners:
        cv2.rectangle(test, (corner[0] - int(ratio * 25), corner[1] - int(ratio * 25)),
        (corner[0] + int(ratio * 25), corner[1] + int(ratio * 25)), (0, 255, 0), thickness=2, lineType=8, shift=0)


    cv2.imshow("Corners Detected", cv2.resize(test, (0, 0), fx=0.5, fy=0.5))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #check if detected markers form roughly parallel lines when connected
    if corners[0][0] - corners[2][0] > epsilon:
        return None

    if corners[1][0] - corners[3][0] > epsilon:
        return None

    if corners[0][1] - corners[1][1] > epsilon:
        return None

    if corners[2][1] - corners[3][1] > epsilon:
        return None

    return corners