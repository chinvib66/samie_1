import cv2
import threading
import datetime
import numpy as np
from .output_files import color_data_img, final_image, OUTPUT_DATA_FOLDER, OUTPUT_VIDEO_FOLDER, path_join
from .color_extractor import extract_colors


class RecordingThread (threading.Thread):
    def __init__(self, name, camera, width=640, height=480):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True
        self.cap = camera
        output_file_path = path_join(OUTPUT_VIDEO_FOLDER, 'outpit.webm')
        fourcc = cv2.VideoWriter_fourcc('V','P','8','0')
        self.out = cv2.VideoWriter(output_file_path ,fourcc, 30, (width,height))

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()


def selfCam():
    camera = cv2.VideoCapture(0)
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


class VideoCamera(object):
    def __init__(self):
        # Open a camera
        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        # Initialize video recording environment
        self.is_record = False
        self.out = None
        self.is_playing = True
        self.is_stopped = False

        # Thread for recording
        self.recordingThread = None
    
    def __del__(self):
        self.cap.release()
        self.is_stopped = True

    def play(self):
        self.is_playing = True
    
    def pause(self):
        self.is_playing = False
    
    def stop(self):
        self.is_playing = False
        self.is_record = False
    # def get_frame(self):
    #     ret, frame = self.cap.read()

    #     if ret:
    #         ret, jpeg = cv2.imencode('.jpg', frame)

    #         # Record video
    #         # if self.is_record:
    #         #     if self.out == None:
    #         #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    #         #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))
                
    #         #     ret, frame = self.cap.read()
    #         #     if ret:
    #         #         self.out.write(frame)
    #         # else:
    #         #     if self.out != None:
    #         #         self.out.release()
    #         #         self.out = None  

    #         return jpeg.tobytes()
      
    #     else:
    #         return None

    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()

    
    def get_frame(self):
        try:
            if self.is_playing:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
        except Exception as e:
            print(e)
            pass
        
            # if ret:
            #     ret, jpeg = cv2.imencode('.jpg', frame)
            #     return jpeg.tobytes()
            # else:
            #     return None
    def get_input_frame(self):
        # if self.is_playing and self.current_frame:
        frame = self.current_frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
        # return None
            
    def get_output_frame(self):
        # if self.is_playing and self.current_frame:
        frame = self.current_frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
        #return None

    def get_data_frame(self):
        # if self.is_playing and self.current_frame:
        frame = self.current_frame
        colors, percentage = extract_colors(frame)
        data_frame = color_data_img(colors, percentage)
        ret, jpeg = cv2.imencode('.jpg', data_frame)
        return jpeg.tobytes()
        # return None
    def final_image(self):
        frame = self.current_frame
        input_img = frame
        output_img = frame
        input_img = cv2.resize(input_img[60:420, :], (512,288), interpolation=cv2.INTER_AREA)
        output_img = cv2.resize(output_img[60:420, :], (512,288), interpolation=cv2.INTER_AREA)
        colors, percentage = extract_colors(input_img)
        data_img = color_data_img(colors, percentage)
        img = np.full((620,1080, 3),255,np.uint8)
        img[0:312, 0:1080] = data_img
        img[315:603, 14:526] = input_img
        img[315:603, 554:1066] = output_img
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()
