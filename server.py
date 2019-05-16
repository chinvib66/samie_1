# System Imports
import os
from flask import Flask, jsonify, url_for, send_from_directory, Response, request
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_socketio import SocketIO

# Custom Imports
from  processes.output_files import gen_color_data_video, init_paths

# Important Variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR,'uploads')
OUTPUT_VIDEO_FOLDER = os.path.join(BASE_DIR,'output/video')
OUTPUT_DATA_FOLDER = os.path.join(BASE_DIR,'output/data')

# App Configurations
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_VIDEO_FOLDER'] = OUTPUT_VIDEO_FOLDER
app.config['OUTPUT_DATA_FOLDER'] = OUTPUT_DATA_FOLDER
CORS(app)
socketio = SocketIO(app)

# Route Definitions


@app.route('/apiv1/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/apiv1/output/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['OUTPUT_VIDEO_FOLDER'],
                               filename)


@app.route('/apiv1/data/<filename>')
def data_file(filename):
    return send_from_directory(app.config['OUTPUT_DATA_FOLDER'],
                               filename)

@app.route('/apiv1/start/<filename>')
def start_process(filename):
    output = gen_color_data_video(filename)
    return jsonify({'url': url_for('data_file', filename=output)})


@app.route('/apiv1/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'status': False, 'msg': 'No File'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': False, 'msg': 'No File'})
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({
                            'url': (url_for('uploaded_file', filename=filename)),
                            'filename':filename,
                            'status': True,
                            'msg': 'File Uploaded Successfully'
                            })
    return jsonify({'status': False, 'msg': 'Invalid Method'})

# @socketio.on('start_p')
# def start_processing(filename, width):
#     return None



# App Run
if __name__ == '__main__':
    # app.run(host='0.0.0.0', threaded=True)
    init_paths(BASE_DIR, UPLOAD_FOLDER, OUTPUT_VIDEO_FOLDER, OUTPUT_DATA_FOLDER)
    socketio.run(app, debug=True)