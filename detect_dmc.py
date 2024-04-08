import numpy as np
import cv2
from PIL import Image
from urllib.request import urlopen


def detect(path):
    global image
    well = np.array(Image.open(path))
    well = cv2.cvtColor(well, cv2.COLOR_BGRA2GRAY)

    harris = cv2.cornerHarris(well, 4, 1, 0.00)
    cv2.imwrite('b.jpg', harris)

    x, thr = cv2.threshold(harris, 0.1 * harris.max(), 255, cv2.THRESH_BINARY)
    thr = thr.astype('uint8')
    cv2.imwrite('c.jpg', thr)

    contours, hierarchy = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(cv2.convexHull(x)) for x in contours]
    max_i = areas.index(max(areas))
    d = cv2.drawContours(np.zeros_like(thr), contours, max_i, 255, 1)
    cv2.imwrite('d.jpg', d)

    rect = cv2.minAreaRect(contours[max_i])
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    e = cv2.drawContours(well,[box], 0 , 1, 0)
    cv2.imwrite('e.jpg', e)
    image = e
    return well