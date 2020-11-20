"""
This file reads an image and processes it:
    - version 1 finding needle object from image
    - version 2 finding orientation of image

OpenCV-package required

Authors:
    Florens Helfferich       F.J.Helfferich@student.tudelft.nl
    Bram Pronk               I.B.Pronk@student.tudelft.nl
"""

import cv2
import numpy as np


def reduce_size(in_image, scale_percent):
    """"
    Reduces the resolution of the image
    output is another image of the same type
    """
    height, width = in_image.shape
    new_height = int(height * scale_percent / 100)
    new_width = int(width * scale_percent / 100)
    dsize = (new_width, new_height)

    return cv2.resize(in_image, dsize, interpolation=cv2.INTER_CUBIC)


def line_detect(in_image, lines_on_image, lower_threshold, upper_threshold, theta_res, min_votes, minLL, maxLG, lpf='no', show='no'):
    """"
    Creates edge mask from in_image and does Hough line detection on the mask
    thresholds: are for the Canny edge mask creation
    lpf: optional setting to use a smoothing filter (low-pass filter) on the image
    show: optional setting to show the edges mask
    """
    # smoothing image against dust particles
    if lpf == 'yes':
        kernel = np.ones((3,3),np.float32)/9
        in_image = cv2.filter2D(in_image,-1,kernel)

    edges = cv2.Canny(in_image, lower_threshold, upper_threshold)
    if show == 'yes':
        cv2.imshow("edge mask", edges)
    lines = cv2.HoughLinesP(edges, 1, np.pi/theta_res, min_votes, minLineLength=minLL, maxLineGap=maxLG)

    for line in lines:
        x1,y1,x2,y2 = line[0]
        cv2.line(lines_on_image, (x1, y1), (x2, y2), (200, 100, 200), 2)

    return lines


org_image = cv2.imread(r'C:\Users\flore\Documents\Uni\brachyosaurus\src\image_pos\photos\bending.jpg')
gray = cv2.cvtColor(org_image, cv2.COLOR_BGR2GRAY)
gray_small = reduce_size(gray, 25)
small_color = cv2.cvtColor(gray_small, cv2.COLOR_GRAY2BGR)

lines = line_detect(gray_small, small_color, 150, 210, 180, 50, 20, 10, 'yes', 'yes')

cv2.imshow('org_image', small_color)
if cv2.waitKey(0) == 13:
    cv2.destroyAllWindows()

