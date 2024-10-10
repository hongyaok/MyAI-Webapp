from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
from function.transcribe import Transcribe

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def homepage():
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return render_template('index.html')

@app.route('/function', methods=['GET', 'POST'])
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


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=False)

