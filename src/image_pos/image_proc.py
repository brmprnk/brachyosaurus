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
image = cv2.imread(r"C:\Users\flore\Documents\Uni\brachyosaurus\src\image_pos\photos\black.jpeg", 0)
rows,cols = image.shape
rot_res = cv2.rotate(image, rotateCode=2)
cv2.imshow('Greyscale', rot_res)
cv2.resizeWindow('Greyscale', (round(0.25*rows), round(0.25*cols)))
if cv2.waitKey(0) == 13:  # 13 is the Enter Key
    cv2.destroyAllWindows()
