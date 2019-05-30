import cv2
import threading
import datetime
import time
import multiprocessing
import numpy as np
from .output_files import color_data_img, final_image, path_join
from .color_extractor import extract_colors


# Important Variables
BASE_DIR = None
UPLOAD_FOLDER = None
OUTPUT_VIDEO_FOLDER = None
OUTPUT_DATA_FOLDER= None
RECORD_FOLDER = None
def init_path_2(a, b, c, d):
    global BASE_DIR
    BASE_DIR = a
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = b
    global OUTPUT_VIDEO_FOLDER
    OUTPUT_VIDEO_FOLDER = c
    global OUTPUT_DATA_FOLDER
    OUTPUT_DATA_FOLDER = d
    global RECORD_FOLDER
    RECORD_FOLDER = path_join(BASE_DIR, 'record')


class RecordingThread (threading.Thread):
    def __init__(self, camera, width=640, height=480):
        global RECORD_FOLDER
        threading.Thread.__init__(self)
        self.isRunning = True
        self.camera = camera
        # Output initialisation
        fps = self.camera.cap.get(cv2.CAP_PROP_FPS)
        print(fps)
        output_file_path = path_join(RECORD_FOLDER, 'output.webm')
        fourcc = cv2.VideoWriter_fourcc('V','P','8','0')
        self.out = cv2.VideoWriter(output_file_path ,fourcc, fps, (width,height))

    def run(self):
        while self.isRunning:
            # ret, frame = self.camera.read()
            # if ret:
            #     self.out.write(frame)
            self.out.write(self.camera.current_frame)
        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self):
        # Open a camera
        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.is_playing = True
        self.is_stopped = False
        # Initialize video recording environment
        self.is_record = False
        # Thread for recording
        self.out=None
        self.recordingThread = None
        self.recordingProcess = None
    
    def __del__(self):
        self.cap.release()
        self.is_stopped = True

    def play(self):
        self.is_playing = True
    
    def pause(self):
        self.is_playing = False
    
    def stop(self):
        filename = None
        if self.is_record:
            filename = self.stop_record()
            print(filename)
        time.sleep(.2)
        self.is_playing = False
        self.is_record = False
        return filename

    def start_record_t(self):
        self.is_record = True
        self.recordingThread = RecordingThread(self)
        self.recordingThread.start()

    def stop_record_t(self):
        self.is_record = False
        if self.recordingThread != None:
            self.recordingThread.stop()
            return 'output.webm'
        return None
    
    def writer(self, cap):
        while self.is_record:
            self.out.write(cap.current_frame)
        self.out.release()

    def start_record(self):
        fourcc = cv2.VideoWriter_fourcc('V','P','8','0')
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        global RECORD_FOLDER
        output_file_path = path_join(RECORD_FOLDER, 'output.webm')
        self.out=cv2.VideoWriter(output_file_path ,fourcc, fps, (640,480))
        self.is_record = True
        # return None
        # try:
        #     # self.recordingProcess = multiprocessing.Process(target=self.writer, args=(self.cap,))
        #     # self.recordingProcess.start()
        # except Exception as e:
        #     print('multip err',e)

    def stop_record(self):
        self.is_record = False
        self.out.release()
        # if self.recordingProcess != None:
        #     self.recordingProcess.join()
        return 'output.webm'
        # return None
    

    def get_frame(self):
        try:
            if self.is_playing:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    if self.is_record:
                        self.out.write(frame)
        except Exception as e:
            print(e)
            pass
        
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

    ### Different frames as streams
    def get_input_frame(self):
        frame = self.current_frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
            
    def get_output_frame(self):
        frame = self.current_frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_data_frame(self):
        frame = self.current_frame
        colors, percentage = extract_colors(frame)
        data_frame = color_data_img(colors, percentage)
        ret, jpeg = cv2.imencode('.jpg', data_frame)
        return jpeg.tobytes()
