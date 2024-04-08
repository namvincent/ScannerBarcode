import cv2 as cv
from cv2 import EVENT_LBUTTONDOWN
from datetime import datetime

# Initialize variables to store the coordinates of the selected area
top_left = None
bottom_right = None
drawing = False
original_image = None
done = False
qty: int = 0
areas = []
# Get the current date and time
current_datetime = datetime.now()

# Convert it to a string
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


def draw_rectangle(event, x, y, flags, param):
    global top_left, bottom_right, drawing, done, image, qty, areas, temp

    

    if event == EVENT_LBUTTONDOWN:

        image = image.copy()
        temp = image.copy()
        if not drawing:
            top_left = (x, y)
            drawing = True
            cv.rectangle(temp, top_left, top_left, (0, 255, 0), 2)
            cv.imshow(current_datetime_str, temp)
        if drawing:
            bottom_right = (x, y)
            cv.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv.imshow(current_datetime_str, image)

    elif event == cv.EVENT_MOUSEMOVE:
        if drawing:
            temp = image.copy()
            bottom_right = (x, y)
            cv.rectangle(temp, top_left, bottom_right, (0, 255, 0), 2)
            cv.imshow(current_datetime_str, temp)

    elif event == cv.EVENT_LBUTTONUP:
        drawing = False
        original_image = temp.copy()
        bottom_right = (x, y)
        cv.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv.imshow(current_datetime_str, image)
        if top_left == bottom_right:
            done = True
            return

        print(
            f"Selected area coordinates: Top Left = {top_left}, Bottom Right = {bottom_right}"
        )

        if top_left is not None:
            areas.append((top_left, bottom_right))
        qty = qty + 1
        top_left = None
        # return top_left, bottom_right
        # If you want to print the coordinates of all pixels within the area
        # print("Coordinates of all pixels within the selected area:")
        # for y in range(top_left[1], bottom_right[1]):
        #     for x in range(top_left[0], bottom_right[0]):
        #         print(f"(x, y) = ({x}, {y})")


def doNothing():
    print("test")


global first

first = True


def select(image_path):
    global top_left, bottom_right, drawing, original_image, done, image, first, temp
    done = False
    # Read the image
    image = cv.imread(image_path)
    temp = image.copy()
    cv.startWindowThread()
    cv.namedWindow(current_datetime_str, cv.WINDOW_AUTOSIZE | cv.WINDOW_FULLSCREEN | cv.WINDOW_KEEPRATIO)

    cv.setMouseCallback(current_datetime_str, draw_rectangle)
    while True:
        cv.imshow(current_datetime_str, image)
        if cv.waitKey(1) & 0xFF == ord("q") or done:
            break

    first = False
    cv.destroyAllWindows()
    return areas
