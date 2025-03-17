from flask import Flask, request, jsonify, Response
import os
# import tempfile
from werkzeug.utils import secure_filename

from utils.config import config
import utils.call_ai as ai

PROMPT_TEXT = """
Extract the table in the document as a CSV with header followed by data.
Use the '|' character as your CSV separator instead of comma, ','.
Keep the empty cells, but don't put zeros in them.
Make sure all rows in the CSV have the same number of cells.

Extract cells as numbers, not text, when possible.
For example, extract "$10,000.00" as 10000.00 and "20%" as 20.
Be extra careful to identify '%' columns, recognizing '%' characters.
Our single table may span multiple tables on multiple pages: append them all together into a single table.
Do not extract text outside the CSV.
Do not add any explanatory text outside of the CSV.
"""

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


@app.route('/ocr', methods=['POST'])
@api_bp.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    prompt_text = PROMPT_TEXT or request.form.get('prompt_text', '')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Get the file name and content
        file_name = secure_filename(file.filename)
        file_blob = file.read()
        
        # Call the function to extract text from the file
        csv_text = ai.gemini_extract_text(file_blob, file_name, prompt_text)
        
        # Return the CSV content directly
        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={os.path.splitext(file_name)[0]}.csv"}
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