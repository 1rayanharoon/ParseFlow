from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
import requests
import json
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ChatDoc API Configuration
API_KEY = "API_KEY_HERE"  # Replace with your actual API key
UPLOAD_URL = "https://api.chatdoc.com/api/v2/documents/upload"
DOCUMENT_URL = "https://api.chatdoc.com/api/v2/documents/{document_id}"
PDF_PARSER_URL = "https://api.chatdoc.com/api/v2/pdf_parser/{document_id}"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}

STATUS_LABELS = {
    1: "UN_PARSED",
    10: "LINK_UN_PARSED",
    12: "PARSING",
    15: "LINK_DOWNLOADING",
    20: "PDF_CONVERTING",
    30: "PDF_CONVERTED",
    40: "TEXT_PARSING",
    50: "ELEMENT_PARSING",
    70: "INSIGHT_CALLBACK",
    210: "TEXT_PARSED",
    300: "ELEMENT_PARSED ✅",
    -1: "TEXT_PARSE_ERROR ❌",
    -2: "ELEMENT_PARSE_ERROR ❌",
    -3: "PDF_CONVERT_ERROR ❌",
    -4: "LINK_DOWNLOAD_ERROR ❌",
    -5: "EXCEED_SIZE_ERROR ❌",
    -6: "EXCEED_TOKENS_ERROR ❌",
    -9: "PAGE_PACKAGE_NOT_ENOUGH_ERROR ❌",
    -10: "PAGE_LIMIT_ERROR ❌",
    -11: "TITLE_COMPLETE_ERROR ❌",
    -12: "READ_TMP_FILE_ERROR ❌",
    -13: "OCR_PAGE_LIMIT_ERROR ❌",
    -14: "CONTENT_POLICY_ERROR ❌",
    -15: "CONTENT_DECODE_ERROR ❌",
    -16: "HTML_CONVERT_ERROR ❌",
    -17: "HTML_EMPTY_BODY_ERROR ❌",
    -18: "HTML_PARSE_ERROR ❌",
    -19: "HTML_DOWNLOAD_ERROR ❌",
    -25: "PACKAGE_NOT_ENOUGH_ERROR ❌"
}

SUCCESS_STATUSES = [300]
ERROR_STATUSES = [code for code in STATUS_LABELS if code < 0]
PROCESSING_STATUSES = [1, 10, 12, 15, 20, 30, 40, 50, 70, 210]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_document_to_chatdoc(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {
            "package_type": "elite",
            "ocr": "auto"
        }
        resp = requests.post(UPLOAD_URL, headers=HEADERS, files=files, data=data)
        resp.raise_for_status()
        document_id = resp.json().get("data", {}).get("id")
        if not document_id:
            raise ValueError("Upload failed: no document ID returned.")
        return document_id

def wait_for_parsing(document_id, max_wait=300, interval=10):
    url = DOCUMENT_URL.format(document_id=document_id)
    waited = 0
    
    while waited <= max_wait:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        response_data = resp.json()
        data = response_data.get("data", {})
        status = data.get("status")
        status_label = STATUS_LABELS.get(status, "Unknown")
        
        if status in SUCCESS_STATUSES:
            return data
        if status in ERROR_STATUSES:
            raise ValueError(f"Parsing failed with status {status}: {status_label}")
        
        time.sleep(interval)
        waited += interval
    
    raise TimeoutError(f"Document not parsed in {max_wait}s")

def get_parsed_content(document_id):
    url = PDF_PARSER_URL.format(document_id=document_id)
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code == 200:
        return resp.json()
    else:
        raise ValueError(f"Failed to fetch parsed content: {resp.text}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Process the document
            document_id = upload_document_to_chatdoc(temp_path)
            parsed_data = wait_for_parsing(document_id)
            parsed_content = get_parsed_content(document_id)
            
            # Clean up temporary file
            os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'document_id': document_id,
                'parsed_data': parsed_content
            })
            
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<document_id>')
def get_status(document_id):
    try:
        url = DOCUMENT_URL.format(document_id=document_id)
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        
        response_data = resp.json()
        data = response_data.get("data", {})
        status = data.get("status")
        status_label = STATUS_LABELS.get(status, "Unknown")
        
        return jsonify({
            'status': status,
            'status_label': status_label,
            'is_complete': status in SUCCESS_STATUSES,
            'is_error': status in ERROR_STATUSES
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)