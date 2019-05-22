import cv2
import numpy as np
from .base_camera import BaseCamera
from .output_files import color_data_img, final_image
from .color_extractor import extract_colors


class Camera(BaseCamera):
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        ### 15 fps probable
        t = 0
        while t < 150:
            # read current frame
            _, img = camera.read()
            colors, percentage = extract_colors(img)
            data_img = color_data_img(colors, percentage)
            input_img = img
            output_img = img
            img = final_image(data_img, input_img, output_img)
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
            t= t+1
        camera.release()
