"""
This file finds the X,Y coordinates of the needle using the tasks:
    - taken photo
    - image processing
    - returning X,Y positions
"""

import cv2
import matplotlib.pyplot as plt
import numpy


cap = cv2.VideoCapture('http://192.168.43.1:8080/video')

i = 0
while True:
    i = i +1
    ret, pic = cap.read()
    if ret:
        print(pic)
        cv2.imshow('bier', pic)
