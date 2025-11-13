import os
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from ocr import pdf_to_text, image_to_text
from summarizer import summarize_text
from report_pdf import text_to_pdf

load_dotenv()

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
SUMMARY_FOLDER = os.getenv('SUMMARY_FOLDER', 'summaries')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        ext = filename.rsplit('.', 1)[1].lower()
        try:
            if ext == 'pdf':
                text = pdf_to_text(save_path)
            else:
                text = image_to_text(save_path)
        except Exception as e:
            return jsonify({'error': 'OCR failed', 'details': str(e)}), 500

        txt_name = filename + '.txt'
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_name)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)

        short = request.form.get('length', 'short')
        try:
            summary = summarize_text(text, mode=short)
        except Exception as e:
            return jsonify({'error': 'Summarization failed', 'details': str(e)}), 500

        summary_filename = filename + '.summary.txt'
        summary_path = os.path.join(SUMMARY_FOLDER, summary_filename)
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        download_url = url_for('download_summary', filename=summary_filename)
        return jsonify({
            'text_file': txt_name, 
            'summary_file': summary_filename, 
            'summary_text': summary,
            'download_url': download_url
        })
    else:
        return jsonify({'error': 'File type not allowed'}), 400


@app.route('/summaries/<path:filename>')
def download_summary(filename):
    return send_from_directory(SUMMARY_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
