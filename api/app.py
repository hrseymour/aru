from flask import Flask, request, jsonify, Response
import os
from werkzeug.utils import secure_filename

from utils.config import config
from utils.scraper import site_scraper
import utils.call_ai as ai

app = Flask(__name__)
app.url_map.strict_slashes = False

# Create a blueprint for api routes
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@app.route('/add', methods=['POST'])
@api_bp.route('/add', methods=['POST'])
def add_numbers():
    data = request.get_json()
    
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({"error": "Missing required parameters 'a' and 'b'"}), 400
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        result = a + b
        return jsonify({"result": result})
    except ValueError:
        return jsonify({"error": "Parameters 'a' and 'b' must be numbers"}), 400


def get_mimetype(file_ext):
    mime_types = {
        "txt": "text/plain",
        "csv": "text/csv", 
        "md": "text/markdown"
    }
    return mime_types.get(file_ext, "text/plain")  # Default to text/plain if extension not found


def call_ai(model, file_blob, file_name, prompt_text):
    # Call the function to extract text from the file
    if model == "OpenAI":
        output_text = ai.openai_extract_text(file_blob, file_name, prompt_text)
    elif model == "Mistral":
        output_text = ai.mistral_extract_text(file_blob, file_name, prompt_text)
    else:
        output_text = ai.gemini_extract_text(file_blob, file_name, prompt_text)
    
    return output_text

@app.route('/ocr', methods=['POST'])
@api_bp.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    prompt_text = request.form.get('prompt_text', '')
    file_ext = request.form.get('file_ext', '')
    model = request.form.get('model', config['API']['DefaultModel'])
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Get the file name and content
        file_name = secure_filename(file.filename)
        file_blob = file.read()
        
        # Call the function to extract text from the file
        output_text = call_ai(model, file_blob, file_name, prompt_text)
       
        # Return the CSV content directly
        return Response(
            output_text,
            mimetype=get_mimetype(file_ext),
            headers={"Content-disposition": f"attachment; filename={os.path.splitext(file_name)[0]}.{file_ext}"}
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/summary', methods=['POST'])
@api_bp.route('/summary', methods=['POST'])
def summary():
    # Check if URL is provided
    url = request.form.get('url', '')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    prompt_text = request.form.get('prompt_text', '')
    file_ext = request.form.get('file_ext', '')
    model = request.form.get('model', config['API']['DefaultModel'])
    
    try:
        return_code, site_text, file_name = site_scraper(url)
        if return_code != 200:
            raise ValueError(site_text)
  
        # Call the function to create summary
        output_text = call_ai(model, site_text, file_name, prompt_text)
                
        # Return the processed content directly
        return Response(
            output_text,
            mimetype=get_mimetype(file_ext),
            headers={"Content-disposition": f"attachment; filename={file_name}.{file_ext}"}
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

# Register the blueprint
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['API']['Port'], debug=True)