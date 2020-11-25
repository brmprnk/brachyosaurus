"""
This file finds the X,Y coordinates of the needle using the tasks:
    - taken photo
    - image processing
    - returning X,Y positions
"""

from queue import LifoQueue
import cv2
from src.util import logger

class ImageAcquisition:
    """
    Class that encapsulates the functionality of retrieving images from a (live) video feed.
    """
    def __init__(self, images_per_second: int, top_camera: str, front_camera: str, no_cam_feed: bool) -> None:
        if top_camera == "" and front_camera == "":
            logger.error("No URL or Path to camera's were given --> Not able to provide visual feedback")
        
        self.top_vidcap = cv2.VideoCapture("http://192.168.43.1:8080/video")
        # TODO: self.front_vidcap = cv2.VideoCapture(front_camera)

        # Convert the nr. of images per second to an amount of frames based on videofeed
        self.images_per_second = self.top_vidcap.get(cv2.CAP_PROP_FPS) * images_per_second
        self.no_cam_feed = no_cam_feed

        self.is_running = True
    
    def retrieve_current_image(self, video_feed: LifoQueue):
        """
        Retrieves the current frame of the video feed.
        """
        logger.info("Video Feed Acquisition has started.")
        while self.is_running:
            success, frame = self.top_vidcap.read()
            if success:
                video_feed.put(frame)
            else:
                logger.error("Not able to retrieve image from VideoCapture Object.")
                
                self.top_vidcap.release()
                cv2.destroyAllWindows()

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
