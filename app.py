from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify, send_from_directory
import os
from function.transcribe import Transcribe
from function.story import prompt_story
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
global port
port = int(os.environ.get('PORT', 5000))
IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'creatorgallery')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def homepage():
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return render_template('index.html')

@app.route('/audtotext', methods=['GET', 'POST'])
def audtotext():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            print(f"File saved as {filename}")
            callfunc = Transcribe()
            extracted_text = callfunc.transcribe(filename)


            txt_filename = filename.rsplit('.', 1)[0] + '.txt'
            with open(txt_filename, 'w') as f:
                f.write(extracted_text)

            return render_template('audtotext.html', text=extracted_text, txt_filename=os.path.basename(txt_filename))

    return render_template('audtotext.html')

@app.route('/texttoimg', methods=['GET', 'POST'])
def texttoimg():
    if request.method == 'POST':
        text = request.form.get('inputText')

        if text:
            img_filename = prompt_story(text, 0, 'uploads')  
            return render_template('texttoimg.html', img_filename=os.path.basename(img_filename), story=text)
        else:
            return "No text entered", 400

    return render_template('texttoimg.html')

@app.route('/creators_gallery')
def creators_gallery():
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    size_classes = ['random-size-small', 'random-size-medium', 'random-size-large']
    images = [
        {
            'filename': img,
            'size_class': random.choice(size_classes)  
        }
        for img in image_files
    ]
    random.shuffle(images)
    return render_template('creators_gallery.html', images=images)

@app.route('/creatorgallery/<filename>')
def gall_file(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)

