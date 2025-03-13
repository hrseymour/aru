from flask import Flask, request, jsonify

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

@app.route('/health', methods=['GET'])
@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

# Register the blueprint
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)