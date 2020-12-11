"""
This file finds the X,Y coordinates of the needle and the orientation of its tip using steps:
    - Retrieve photo frame from video feed
    - Process image
    - Return data to Main Program Loop
"""
from queue import Queue
import time
import multiprocessing
import cv2
from src.util import logger
from src.image_proc2 import position_from_image

class ImageAcquisition:
    """
    Class that encapsulates the functionality of retrieving images from a (live) video feed.
    The video feed is shown to the user using the OpenCV imshow() functionality.

    The user defines the number of times per second the video footage is used to calculate position,
    and these frames are then processed to obtain a needle tip position and orientation.

    Needle tip position and orientation is communicated back to the Main Process.

    Attributes
    ----------
    top_vid_link : str
        Link or path to video feed of the top camera
    images_per_second : int
        Number that represents the number of times per second a video frame is processed to determine needle pos/ori
    no_cam_feed : bool
        Boolean from input args that determines if the live video stream is displayed.
    is_running : bool
        Boolean that can be used to signal the termination of Processes that use this Class.
    """

    def __init__(self, images_per_second: int, top_camera: str, front_camera: str, no_cam_feed: bool) -> None:
        if top_camera == "" and front_camera == "":
            logger.error(
                "No URL or Path to camera's were given --> Not able to provide visual feedback")

        self.top_vid_link = "http://192.168.43.1:8080/video"

        self.images_per_second = images_per_second
        self.no_cam_feed = no_cam_feed

        self.is_running = True  # Bool to be modified from main loop, that ends loop

    def retrieve_current_image(self, needle_pos_feed: multiprocessing.Queue) -> None:
        """ Retrieves and processes video feed, then sends needle pos/ori back to main Process.

        Parameters
        ----------
        needle_pos_feed : multiprocessing.Queue
            Queue to pass needle position and orientation to main Process.

        Raises
        ------
        OpenCV Error
            Could not connect to video stream from file

        Returns
        -------
        None
        """

        # Create Queue of size 10 that is used for image acq/proc
        video_feed = Queue(maxsize=10)

        top_vidcap = cv2.VideoCapture(self.top_vid_link)

        process_frame = self.fps_to_images_per_second(top_vidcap.get(cv2.CAP_PROP_FPS))

        while self.is_running:
            # Image Acquisition
            frame_nr = top_vidcap.get(1)  # Current frame of the video feed
            success, frame = top_vidcap.read() # Retrieve frame from video feed

            if success:
                # If camera feed is shown (nofeed == false)
                if not self.no_cam_feed:

                    cv2.imshow("Top Camera Feed", frame)

                    if cv2.waitKey(1) == 27:  # Escape Key exits loop
                        logger.error("Exiting Video Acquisition Process.")
                        top_vidcap.release()
                        cv2.destroyAllWindows()
                        # Sentinel Value to end main program loop
                        needle_pos_feed.put((None, None))
                        break

                # Only send a certain few frames per second to processing
                if frame_nr % process_frame == 0:
                    video_feed.put(frame)

            else:
                logger.error("Not able to retrieve image from VideoCapture Object. Exiting Process.")
                top_vidcap.release()
                cv2.destroyAllWindows()
                needle_pos_feed.put((None, None)) # Can't open video feed, send Sentinel value to Main Process
                break

            # Image Processing
            if not video_feed.empty(): # Check queue if an image can be processed

                current_frame = video_feed.get()

                # Retrieve needle tip and orientation and measure processing time.
                start = time.time()
                tip_position, tip_ori = position_from_image(
                    current_frame, "config.ini", flip='yes', filtering='yes', show='yes')
                end = time.time()

                logger.success("processing took {}".format((end - start)))

                if tip_position is None or tip_ori is None: # No lines detected, so don't get pos and ori
                    continue

                # Send Needle position and orientation back to main process.
                needle_pos_feed.put((tip_position, tip_ori))

    def fps_to_images_per_second(self, video_fps: int) -> int:
        """ Calculates the Number of images per second sent to processing, expressed in nr of frames between images.
        (So 25 fps and 2 images per second leads to one image every 12 frames, for example)

        Parameters
        ----------
        video_fps : int
            The frames per second of the opened video feed

        Returns
        -------
        The number of times per second a frame will be sent to processing.
        """
        return video_fps / self.images_per_second
