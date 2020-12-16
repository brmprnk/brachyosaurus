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


def reduce_size(in_image, scale_percent=50):
    """
    Reduces the resolution of the image
        output is another image of the same type (ndarray)
    """
    height = int(in_image.shape[0])
    width = int(in_image.shape[1])
    new_height = int(height * scale_percent / 100)
    new_width = int(width * scale_percent / 100)
    dsize = (new_width, new_height)
    return cv2.resize(in_image, dsize, interpolation=cv2.INTER_CUBIC)


def lpf(in_image, size_blur=3):
    """
    Low pass filtering the image
        used in position_from_image if lpf argument is 'yes'
        output is another image of the same type (ndarray)
    """
    if size_blur < 3:
        size_blur = 3
    kernel = np.ones((size_blur, size_blur), np.float32) / (size_blur*size_blur)
    return cv2.filter2D(in_image, -1, kernel)


def orientation(line: tuple, mid_height: int) -> (float, float):
    """"
    Finds the orientation of a given line (x1, y1, x2, y2)
        used in position_from_image as one of its outputs
        returns the x-direction and y-direction separately as if each line is a vector in 2D
    """
    x1 = line[0]
    y1 = line[1] - mid_height
    x2 = line[2]
    y2 = line[3] - mid_height
    abs_r = sqrt((x2-x1)**2 + (y2-y1)**2)
    return (x2-x1)/abs_r, (y2-y1)/abs_r


def line_numbering(in_image, lines_array):
    """"
    Numbers the lines and puts them in the given 'in_image' image
        used in position_from_image when the argument show is 'yes'
        output is another image of the same type (ndarray)
    """
    lines = lines_array
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    lightblue = (255, 255, 0)
    thickness = 1
    for i in range(len(lines)):
        xi = lines[i, 2]
        yi = lines[i, 3]
        origin = (xi, yi)
        in_image = cv2.putText(in_image, str(i), origin, fontFace=font, fontScale=fontScale, color=lightblue, thickness=thickness, lineType=cv2.LINE_AA, bottomLeftOrigin=False)
    return in_image


def position_from_image(in_image, configpath: str, flip='no', filtering='no', show='no') -> (tuple, tuple):
    """
    Version 1: provides position feedback by just returning x2 y2 of last line and its orientation (tip_pos, tip_dir)
        - in_image: the path to the image or the image itself from which the position is read
        - configpath: the path to the config file with all image processing settings
        - filtering (optional): 'yes' if a 3x3 low-pass filter improves line detection see 'lpf' function above
        - show (optional): 'yes' if all numbered lines and orientation of tip need to be shown in the original image
    """
    # Read image, convert to grayscale and reduce resolution for calculation speed
    if type(in_image) == str:
        in_image = cv2.imread(in_image)
    in_image = cv2.cvtColor(in_image, cv2.COLOR_BGR2GRAY)
    in_image = reduce_size(in_image, 40)
    # flipping along vertical axis (left becomes right)
    if flip == 'yes':
        in_image = cv2.flip(in_image, 1)

    # Read required values from config.ini file
    config_object = ConfigParser()
    config_object.read(configpath)
    imagepos = config_object["IMAGEPOS"]
    # for edge detection:
    lower_threshold = int(imagepos["lower_threshold"])
    upper_threshold = int(imagepos["upper_threshold"])
    # for line detection from edge mask:
    theta_resolution = int(imagepos["theta_resolution"])
    min_votes = int(imagepos["min_votes"])
    minll = int(imagepos["minll"])
    maxlg = int(imagepos["maxlg"])
    minlines = int(imagepos["minimum_lines"])

    # lpf filtering if selected see 'lpf' function above
    if filtering == 'yes':
        in_image = lpf(in_image)

    # creating edge mask then performing line detection
    edge_mask = cv2.Canny(image=in_image, threshold1=lower_threshold, threshold2=upper_threshold)
    N = 0
    i = 0
    while N < minlines:
        i = i + 1
        lines = cv2.HoughLinesP(edge_mask, 1, np.pi / theta_resolution, min_votes, minLineLength=minll, maxLineGap=maxlg)
        min_votes = min_votes - 5
        minll = minll - 1
        if min_votes < 0 or minll < 0:
            print("image_proc: no lines found by decrementing params !!!")
            break
        if lines is None:
            N = 0
        else:
            N = len(lines[:, 0, 0])
        print("image_proc: iteration " + str(i) + " finished, "+str(N)+" lines found --> decremented params")

    # sorting lines by smallest x1 coord
    if lines is None:
        return None, None

    sorting_ind = np.argsort(lines[:, 0, 0])
    sorted_lines = np.zeros((len(lines[:, 0, 0]), 4), dtype='int16')
    for i in range(len(lines[:, 0, 0])):
        row_to_append = np.array(lines[sorting_ind[i], 0, :], dtype='int16')
        sorted_lines[i, :] = row_to_append
    if len(sorted_lines[:, 0]) < 30:
        print("image_proc2: " + str(len(sorted_lines[:, 0])) + " lines detected -> sorted_lines = \n", sorted_lines)
    else:
        print("image_proc2: Too many lines to print (" + str(len(sorted_lines[:, 0])) + " lines detected)")

    # position calculation returning (x2, y2) of last line, (x_orientation, y_orientation)
    # y orientation with respect to the mid horizontal line
    y_mid = int(in_image.shape[0]/2)
    tip_dir = orientation(sorted_lines[-1, :], y_mid)

    tip_pos = (sorted_lines[-1, 2], sorted_lines[-1, 3])

    # ---------------------------- SHOW PART --------------------------------
    # showing lines in gray of original image if requested by 'show' argument
    if show == 'yes':
        small_color = cv2.cvtColor(in_image, cv2.COLOR_GRAY2BGR)
        purple = (200, 100, 200)
        yellow = (0, 255, 255)
        # putting lines in image
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(small_color, (x1, y1), (x2, y2), purple, 2)
        # putting numbers and direction arrow in image
        num_image = line_numbering(small_color, sorted_lines)
        endpoint = (tip_pos[0]+int(40*tip_dir[0]), tip_pos[1]+int(40*tip_dir[1]))
        if endpoint[0] > in_image.shape[1] or endpoint[1] > in_image.shape[0]:
            # reduce endpoint:
            endpoint = (tip_pos[0]+int(10*tip_dir[0]), tip_pos[1]+int(10*tip_dir[1]))
        print("image_proc->show part: endpoint arrow = ", endpoint)
        num_arrow_image = cv2.arrowedLine(num_image, tip_pos, endpoint, yellow, 2)
        cv2.imshow('Numbered Lines', num_arrow_image)
        print("image_proc->show part: Press enter to stop showing image(s)")
        if cv2.waitKey(1) == 13:
            cv2.destroyAllWindows()

    return tip_pos, tip_dir
