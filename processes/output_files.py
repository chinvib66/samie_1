# Imports
import os
import cv2
import numpy as np

# Custom Imports
from .color_extractor import extract_colors

# Important Variables
BASE_DIR = None
UPLOAD_FOLDER = None
OUTPUT_VIDEO_FOLDER = None
OUTPUT_DATA_FOLDER= None

def init_paths(a, b, c, d):
    global BASE_DIR
    BASE_DIR = a
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = b
    global OUTPUT_VIDEO_FOLDER
    OUTPUT_VIDEO_FOLDER = c
    global OUTPUT_DATA_FOLDER
    OUTPUT_DATA_FOLDER = d


# Functions
# Path join 
def path_join(a, b):
    return os.path.join(a, b)

# Descending Sort by Percentage
def sort_desc(colors, percentage):
    # if len(percentage) is 1:
    #     return colors, percentage
    try:
        zipped = list(zip(colors, percentage))
        def sort_key(val):
            return val[1]
    
        zipped.sort(key=sort_key, reverse=True)
        colors, percentage = zip(*zipped)
        return colors, percentage
    except:
        return colors, percentage

# Creates the Color-Percentage Circle Image
# Returns image (np.ndarray)
def color_data_img(colors, percentage, width=1080, height=312):
    colors, percentage = sort_desc(colors, percentage)
    # if width > 768:
    max_l = 30
    per_row = 10                                                        #per_row = width//104
    # if width < 768:
    #     max_l = 9
    #     per_row = 3                                                   #per_row = width//104
    l = min(max_l, len(percentage))                                     #l = len(percentage)
    rows = 3                                                            #rows = (l//per_row) + 1 ; height = rows*104
    img = np.full((height, width, 3), 255, np.uint8)
    pos_cir = [width+52, height + 52]
    for color, percent, x in zip(colors, percentage, range(l)):
        pos_cir[0] = pos_cir[0] - 104
        if x%per_row is 0:
            pos_cir[1] = pos_cir[1] - 104
            pos_cir[0] = width-52
        img = cv2.circle(img ,(pos_cir[0], pos_cir[1]), 50,  color.tolist(), -1)
        cv2.putText(img, str(percent)+'%', (pos_cir[0]-25,pos_cir[1]+5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
    return img

# Generates Video File
def gen_color_data_video(filename, width=1080, height=312):
    print("Starting Color Data Processing and Video File Generation")
    input_file_path = path_join(UPLOAD_FOLDER, filename)
    cap = cv2.VideoCapture(input_file_path)
    output_file_name = 'color_output_'+filename.split('.')[0]+'.webm'
    output_file_path = path_join(OUTPUT_DATA_FOLDER, output_file_name)
    output = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc('V','P','8','0'), 30, (width, height))
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            colors, percentages = extract_colors(frame)
            img = color_data_img(colors, percentages, width, height)
            output.write(img)
        else:
            break
    cap.release()
    output.release()
    print('Color Data Output File Generated')
    return output_file_name
    # Web Socket emit
    # send url_for('data_file', out_name)

def gen_output_video(filename):
    print("Starting Video Processing and Output Video File Generation")
    input_file_path = path_join(UPLOAD_FOLDER, filename)
    cap = cv2.VideoCapture(input_file_path)
    output_file_name = 'video_output_'+filename.split('.')[0]+'.webm'
    output_file_path = path_join(OUTPUT_VIDEO_FOLDER, output_file_name)
    output = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc('V','P','8','0'), 30, (int(cap.get(3)), int(cap.get(4))))
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            
            output.write(frame)
        else:
            break
    cap.release()
    output.release()
    print('Video Output File Generated')
    return output_file_name


# Live Stream
def final_image(frame):
    colors, percentage = extract_colors(frame)
    data_img = color_data_img(colors, percentage)
    input_img = frame
    output_img = frame
    img = np.full((620,1080, 3),255,np.uint8)
    img[0:312, 0:1080] = data_img
    input_img = cv2.resize(input_img[60:420, :], (512,288), interpolation=cv2.INTER_AREA)
    output_img = cv2.resize(output_img[60:420, :], (512,288), interpolation=cv2.INTER_AREA)
    img[315:603, 14:526] = input_img
    img[315:603, 554:1066] = output_img
    return img