"""
This file finds the X,Y coordinates of the needle using the tasks:
    - taken photo
    - image processing
    - returning X,Y positions
"""

import cv2
import matplotlib.pyplot as plt
import numpy
import time
from src.util import logger

class ImageAcquisition:
    """
    Class that encapsulates the functionality of retrieving images from a (live) video feed.
    """
    def __init__(self, images_per_second: int, top_camera: str, front_camera: str, show_cam_feed: bool) -> None:
        if top_camera == "" and front_camera == "":
            logger.error("No URL or Path to camera's were given --> Not able to provide visual feedback")
        
        self.top_vidcap = cv2.VideoCapture("http://192.168.43.1:8080/video")
        # TODO: self.front_vidcap = cv2.VideoCapture(front_camera)

        # Convert the nr. of images per second to an amount of frames based on videofeed
        self.images_per_second = self.top_vidcap.get(cv2.CAP_PROP_FPS) * images_per_second
        self.show_cam_feed = show_cam_feed
    
    def retrieve_current_image(self):
        """
        Retrieves the current frame of the video feed.
        """
        success, frame = self.top_vidcap.read()
        if success:
            if self.show_cam_feed:
                cv2.imshow("Top Camera Feed", frame)
                if cv2.waitKey(1) == 13:
                    cv2.destroyAllWindows()
            return frame

        else:
            logger.error("Not able to retrieve image from VideoCapture Object.")
            
            self.top_vidcap.release()
            cv2.destroyAllWindows()

            return None

    def live_image(self):
        """
        Returns the live image of the camera feed.
        """
        frame_nr = self.top_vidcap.get(1) # Current frame of the video feed
        success, frame = self.top_vidcap.read()
        if frame_nr % self.images_per_second == 0: # Only show if the frame corresponds to desired images_per_second
            if success:
                return pic
                # cv2.imshow('bier', pic)
                # if cv2.waitKey(1) == 13:
                #     break
