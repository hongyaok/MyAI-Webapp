from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
from function.transcribe import Transcribe

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def homepage():
    #clear the uploads folder
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return render_template('index.html')

@app.route('/function', methods=['GET', 'POST'])
def audtotext():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            print(f"File saved as {filename}")
            # Here you would process the audio file and extract text (mock processing for now)
            callfunc = Transcribe()
            extracted_text = callfunc.transcribe(filename)

            # Save the extracted text to a .txt file
            txt_filename = filename.rsplit('.', 1)[0] + '.txt'
            with open(txt_filename, 'w') as f:
                f.write(extracted_text)

            # Render the page with the transcribed text and provide a download option
            return render_template('audtotext.html', text=extracted_text, txt_filename=os.path.basename(txt_filename))

    return render_template('audtotext.html')

# Route to download the .txt file
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)

