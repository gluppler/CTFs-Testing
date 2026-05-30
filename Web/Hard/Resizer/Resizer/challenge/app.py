from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, send_file
import os
from utils.resizer import resizer


app = Flask(__name__)
app.secret_key = os.urandom(32)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BLACKLISTED_EXTENTIONS = {'.py', '.pyc'}

CONTENT_TYPE_BLACKLIST = {'application/x-python-code', 'application/x-python-bytecode', 'text/x-python'}


def is_extention_blacklisted(filename):
    for ext in BLACKLISTED_EXTENTIONS:
        if ext in filename:
            return True
        
def is_content_type_blacklisted(content_type):
    return content_type in CONTENT_TYPE_BLACKLIST




@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/resize-image')
def resize_image():
    return render_template('index.html')

@app.route('/resize', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part in the request', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    print(f"Received file: {file.filename}, content type: {file.content_type}")

    if is_extention_blacklisted(file.filename):
        flash('File extension not allowed', 'error')
        return jsonify(message='File extension not allowed'), 403   
     
    if is_content_type_blacklisted(file.content_type):
        flash('File content type not allowed', 'error')
        return jsonify(message='File content type not allowed'),  403 

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return "File already exists. Please rename your file and try again.", 400
    file.save(filepath)

    try:
        resizer(800, 800, "resize", filepath)
        new_resize_path = filepath.rsplit('.', 1)[0] + '_resized.' + filepath.rsplit('.', 1)[1]
        return send_file(
            new_resize_path,
            as_attachment=True,
            download_name=os.path.basename(new_resize_path)
        )
    except Exception as e:
        print(f"Error occurred while resizing image: {e}")
        return jsonify(message='Error occurred while resizing image'), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
