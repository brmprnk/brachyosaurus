"""
This file offers functions related to image processing

OpenCV-package required

Authors:
    Florens Helfferich       F.J.Helfferich@student.tudelft.nl
    Bram Pronk               I.B.Pronk@student.tudelft.nl
"""
import cv2
import numpy as np
from math import sqrt
from configparser import ConfigParser


def read(path):
    return cv2.imread(path)


def reduce_size(in_image, scale_percent=50):
    """
    Reduces the resolution of the image
    output is another image of the same type
    """
    height = int(in_image.shape[0])
    width = int(in_image.shape[1])
    new_height = int(height * scale_percent / 100)
    new_width = int(width * scale_percent / 100)
    dsize = (new_width, new_height)
    return cv2.resize(in_image, dsize, interpolation=cv2.INTER_CUBIC)


def blur(in_image, size_blur=3):
    """Low pass filtering the image"""
    if size_blur < 3:
        size_blur = 3
    kernel = np.ones((size_blur, size_blur), np.float32) / (size_blur*size_blur)
    return cv2.filter2D(in_image, -1, kernel)


def orientation(line, mid_height) -> (float, float):
    x1 = line[0]
    y1 = line[1] - mid_height
    x2 = line[2]
    y2 = line[3] - mid_height
    abs_r = sqrt((x2-x1)**2 + (y2-y1)**2)
    return (x2-x1)/abs_r, (y2-y1)/abs_r


def line_numbering(in_image, lines_array):
    lines = lines_array
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    blue = (255, 255, 0)
    thickness = 1
    for i in range(len(lines)):
        xi = lines[i, 2]
        yi = lines[i, 3]
        origin = (xi, yi)
        in_image = cv2.putText(in_image, str(i), origin, fontFace=font, fontScale=fontScale, color=blue, thickness=thickness, lineType=cv2.LINE_AA, bottomLeftOrigin=False)
    return in_image


def position_feedback(path, configpath, show='no') -> (tuple, tuple):
    """
    Returns x (int), y (int) position and orientation (float) of needle object
        in_image: the image from which the position is read
        configpath: the path to the config file with all image processing settings
        show (optional): 'yes' if all lines need to be shown in the image named 'in_image'

    Version 1: calculates tip pos by just returning x2 y2 and its direction (tip_dir)
    """
    # convert to grayscale
    in_image = cv2.imread(path)
    in_image = cv2.cvtColor(in_image, cv2.COLOR_BGR2GRAY)
    in_image = reduce_size(in_image, 40)
    small_color = cv2.cvtColor(in_image, cv2.COLOR_GRAY2BGR)
    print(in_image)
    print(" type of a in_image = ", type(in_image))
    print(" type of a single cell = ", type(in_image[0, 0]))
    #print(str(in_image.shape[0]) + ' and type is ' + str(type(in_image[0])))

    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(configpath)
    imagepos = config_object["IMAGEPOS"]
    lower_threshold = int(imagepos["lower_threshold"])
    upper_threshold = int(imagepos["upper_threshold"])
    theta_resolution = int(imagepos["theta_resolution"])
    min_votes = int(imagepos["min_votes"])
    minll = int(imagepos["minll"])
    maxlg = int(imagepos["maxlg"])

    # creating edge mask then performing line detection
    edge_mask = cv2.Canny(image=in_image, threshold1=lower_threshold, threshold2=upper_threshold)
    lines = cv2.HoughLinesP(edge_mask, 1, np.pi / theta_resolution, min_votes, minLineLength=minll, maxLineGap=maxlg)
    # sorting lines by smallest x1 coord
    sorting_ind = np.argsort(lines[:, 0, 0])
    sorted_lines = np.zeros((len(lines[:, 0, 0]), 4), dtype='int16')
    for i in range(len(lines[:, 0, 0])):
        row_to_append = np.array(lines[sorting_ind[i], 0, :], dtype='int16')
        sorted_lines[i, :] = row_to_append
    print("image_proc2: sorted_lines = \n", sorted_lines)

    # showing lines in gray of original image if requested
    if show == 'yes':
        purple = (200, 100, 200)
        # putting lines in image
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(small_color, (x1, y1), (x2, y2), purple, 2)
        # putting numbers in image
        num_image = line_numbering(small_color, sorted_lines)
        cv2.imshow('Numbered Lines', num_image)
        print("image_proc: Press enter to stop showing image(s)")
        if cv2.waitKey(0) == 13:
            cv2.destroyAllWindows()

    # position calculation returning (x2, y2) of last line, (x_orientation, y_orientation)
    # y orientation with respect to the mid horizontal line
    y_mid = int(in_image.shape[0]/2)
    tip_dir = orientation(sorted_lines[-1, :], y_mid)

    tip_pos = (sorted_lines[-1, 2], sorted_lines[-1, 3])
    return tip_pos, tip_dir
