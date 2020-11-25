"""
This file finds the X,Y coordinates of the needle using the tasks:
    - taken photo
    - image processing
    - returning X,Y positions
"""
import cv2
from src.util import logger

class ImageAcquisition:
    """
    Class that encapsulates the functionality of retrieving images from a (live) video feed.
    """
    def __init__(self, images_per_second: int, top_camera: str, front_camera: str, no_cam_feed: bool) -> None:
        if top_camera == "" and front_camera == "":
            logger.error("No URL or Path to camera's were given --> Not able to provide visual feedback")
        
        self.top_vid_link = "http://192.168.43.1:8080/video"
        # TODO: self.front_vid_link = front_camera

        self.images_per_second = images_per_second
        self.no_cam_feed = no_cam_feed

        self.is_running = True # Bool to be modified from main loop, that ends loop
    
    def retrieve_current_image(self, video_feed):
        """
        Produces an image feed. This video feed is output to the screen using imshow().
        The user sets the amount of frames the logic uses, that amount of frames is used for
        image processing logic. These frames are added to the video_feed Queue
        """
        top_vidcap = cv2.VideoCapture(self.top_vid_link)
        # Number of images per second expressed in nr of frames between images
        # (so 25 fps and 2 images per second leads to one image every 12 frames, for example)
        produce_image_frame = top_vidcap.get(cv2.CAP_PROP_FPS) / self.images_per_second

        logger.info("Video Feed Acquisition has started.")
        while self.is_running:
            frame_nr = top_vidcap.get(1) # Current frame of the video feed
            success, frame = top_vidcap.read()
            if success:
                # If camera feed is shown (nofeed == false)
                if not self.no_cam_feed:
                    cv2.imshow("Top Camera Feed", frame)
                    if cv2.waitKey(1) == 27: # Escape Key exits loop
                        top_vidcap.release()
                        cv2.destroyAllWindows()
                        video_feed.put(None) # Sentinel Value to end main program loop
                        break
                if frame_nr % produce_image_frame == 0: # Only show if the frame corresponds to desired images_per_second
                    video_feed.put(frame)
            else:
                logger.error("Not able to retrieve image from VideoCapture Object.")
                
                top_vidcap.release()
                cv2.destroyAllWindows()
                video_feed.put(None) # Sentinel Value to end main program loop
                break
