# System Imports
import os
import time
from flask import Flask, jsonify, url_for, send_from_directory, Response, request, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS
# from flask_socketio import SocketIO, Namespace, emit, send
from multiprocessing.pool import ThreadPool

# Custom Imports
from processes.output_files import gen_color_data_video, init_paths, gen_output_video
from processes.camera import VideoCamera, init_path_2
#from processes.camera_1 import VideoCamera, init_path_2


# Important Variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR,'uploads')
OUTPUT_VIDEO_FOLDER = os.path.join(BASE_DIR,'output/video')
OUTPUT_DATA_FOLDER = os.path.join(BASE_DIR,'output/data')
RECORD_FOLDER = os.path.join(BASE_DIR,'record')

# App Configurations
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_VIDEO_FOLDER'] = OUTPUT_VIDEO_FOLDER
app.config['OUTPUT_DATA_FOLDER'] = OUTPUT_DATA_FOLDER
app.config['RECORD_FOLDER'] = RECORD_FOLDER
CORS(app)
# socketio = SocketIO(app)


# Thread definitions
pool = ThreadPool(processes=2)

# Route Definitions

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/apiv1/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/apiv1/output/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['OUTPUT_VIDEO_FOLDER'], filename)


@app.route('/apiv1/data/<filename>')
def data_file(filename):
    return send_from_directory(app.config['OUTPUT_DATA_FOLDER'], filename)


@app.route('/apiv1/record/<filename>')
def record_file(filename):
    return send_from_directory(app.config['RECORD_FOLDER'], filename)


@app.route('/apiv1/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'status': False, 'message': 'No File'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': False, 'message': 'No File'})
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({
                            'url': (url_for('uploaded_file', filename=filename)),
                            'filename':filename,
                            'status': True,
                            'message': 'File Uploaded Successfully'
                            })
    return jsonify({'status': False, 'message': 'Invalid Method'})

@app.route('/apiv1/startProcess/<filename>')
def startProcess(filename):
    try:
        color_data_thread   = pool.apply_async(gen_color_data_video, 
                                                args=(filename,))
        print('Process 1')
        output_video_thread = pool.apply_async(gen_output_video, 
                                                args=(filename,))
        print('Process 2')
        output_data_file    = color_data_thread.get()
        print('Process 1 Done')
        output_video_file   = output_video_thread.get()
        print('Process 2 Done')
        data = {'data_url': url_for('data_file', filename=output_data_file),
                'output_video_url': url_for('processed_file',filename= output_video_file),
                'original_file_url': url_for('uploaded_file', filename=filename),
                'message': 'Processing Completed',
                'status': 1,
                'error':False
                }
        return jsonify(data)
    except Exception as e:
        print('Error ',e)
        return jsonify({'error': True, 'message': e, 'status': 0})



# Live Video Feed


video_camera = None
# global_output_frame = None
# global_input_frame = None
global_data_frame = None

def start_frames():
    global video_camera
    while True:
        video_camera.get_frame()

@app.route('/ondevice/play')
def play():
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
    if video_camera.is_stopped:
        video_camera.__init__()
    video_camera.play()
    return jsonify({'status':'Playing'})


@app.route('/ondevice/pause')
def pause():
    global video_camera
    try:
        video_camera.pause()
        return jsonify({'status':'Paused'})
    except Exception as e:
        return jsonify({'status':e})


@app.route('/ondevice/record')
def record():
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
    
    if video_camera.is_stopped:
        video_camera.__init__()
        video_camera.play()
    try:
        video_camera.start_record()
        return jsonify( {'status':'Recording'})
    except Exception as e:
        return jsonify({'status':e})


@app.route('/ondevice/stop')
def stop():
    global video_camera
    try:
        file = video_camera.stop()
        video_camera.__del__()
        return jsonify({'status':'Stopped', 'file':file})
    except Exception as e:
        return jsonify({'status':e})

def data_input_output():
    global video_camera 
    global global_data_frame

    if video_camera == None:
        video_camera = VideoCamera()
    
    time.sleep(0.5)

    while True:
        video_camera.get_frame()
        frame = video_camera.final_image()

        if frame != None:
            global_data_frame = frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_data_frame + b'\r\n\r\n')

@app.route('/ondevice/view_final_img')
def view_final_img():
    return Response(data_input_output(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# App Run
if __name__ == '__main__':
    init_paths(BASE_DIR, UPLOAD_FOLDER, OUTPUT_VIDEO_FOLDER, OUTPUT_DATA_FOLDER)
    init_path_2(BASE_DIR, UPLOAD_FOLDER, OUTPUT_VIDEO_FOLDER, OUTPUT_DATA_FOLDER)
    app.run(host='0.0.0.0', threaded=True, debug=True)
    # socketio.run(app, debug=True)





## Code for data, input, output as different streams

# def data_stream():
#     global video_camera 
#     global global_data_frame

#     if video_camera == None:
#         video_camera = VideoCamera()
    
#     live_pool.apply_async(start_frames)

#     time.sleep(0.5)

#     while True:
#         frame = video_camera.get_data_frame()

#         if frame != None:
#             global_data_frame = frame
#             yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         else:
#             yield (b'--frame\r\n'
#                             b'Content-Type: image/jpeg\r\n\r\n' + global_data_frame + b'\r\n\r\n')

# @app.route('/ondevice/data_video_viewer')
# def data_video_viewer():
#     return Response(data_stream(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')



# def input_stream():
#     global video_camera 
#     global global_input_frame

#     if video_camera == None:
#         video_camera = VideoCamera()
    
#     time.sleep(1)
#     while True:
#         frame = video_camera.get_input_frame()

#         if frame != None:
#             global_input_frame = frame
#             yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         else:
#             yield (b'--frame\r\n'
#                             b'Content-Type: image/jpeg\r\n\r\n' + global_input_frame + b'\r\n\r\n')

# @app.route('/ondevice/input_video_viewer')
# def input_video_viewer():
#     return Response(input_stream(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


# def output_stream():
#     global video_camera 
#     global global_output_frame

#     if video_camera == None:
#         video_camera = VideoCamera()
    
#     live_pool.apply_async(start_frames)

#     time.sleep(1.5)

#     while True:
#         frame = video_camera.get_output_frame()

#         if frame != None:
#             global_output_frame = frame
#             yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         else:
#             yield (b'--frame\r\n'
#                             b'Content-Type: image/jpeg\r\n\r\n' + global_output_frame + b'\r\n\r\n')

# @app.route('/ondevice/output_video_viewer')
# def output_video_viewer():
#     return Response(output_stream(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

