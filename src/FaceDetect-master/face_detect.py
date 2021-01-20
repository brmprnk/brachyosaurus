"""
face detection using Haar classifiers taken from https://github.com/shantnu/FaceDetect/
 with the goal to learn the python setup for object detection
 - very sensitive to 'detectMultiScale' function params, especially 'scaleFactor'
 - run with "python face_detect.py Andre_Maastricht2020_Still1.jpg" for example


 Original author: Shantnu Tiwari https://github.com/shantnu/
"""

import cv2
import sys

# Get user supplied values
imagePath = sys.argv[1]
cascPath = "haarcascade_frontalface_default.xml"

# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

# Read the image
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect faces in the image
faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=2,
    minNeighbors=4,
    minSize=(30, 30),
    #flags = cv2.cv2.CV_HAAR_SCALE_IMAGE    # made a comment due to not working with higher python or cv version (3+)
)

print("Found {0} faces!".format(len(faces)))

# Draw a rectangle around the faces
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow("Faces found", image)
if cv2.waitKey(0) == 13:
    cv2.destroyAllWindows()

