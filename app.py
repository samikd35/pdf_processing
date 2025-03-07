import utils.session
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import tempfile
from app.utils.pdf_processor import process_pdf
from app.utils.mongo_utils import create_vector_index, store_document
from app.utils.text_extractor import extract_pdf_text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.urandom(24)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            try:
                # Process PDF
                chunks, metadata = process_pdf(file_path)
                
                # Store in MongoDB with embeddings
                document_ids = store_document(chunks, metadata)
                
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'message': f'Successfully processed and stored in database with {len(chunks)} chunks',
                    'document_ids': document_ids
                })
            except Exception as e:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': str(e)
                })
            
            # Clean up temp file
            try:
                os.remove(file_path)
                os.rmdir(temp_dir)
            except:
                pass
        else:
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': 'Invalid file type. Only PDF files are allowed.'
            })
    
    return jsonify(results)

@app.route('/status')
def status():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    # Create vector index if it doesn't exist
    create_vector_index()
    app.run(debug=True)
