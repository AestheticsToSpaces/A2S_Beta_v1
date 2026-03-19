from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from dotenv import load_dotenv

# Load .env file from LLM folder first, then root
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add parent directory to path to import LLM modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.core import process_message, process_vastu
from data.loader import load_product_catalog
from utils.formatters import format_product_summary

app = Flask(__name__)
CORS(app)

# Load catalog once at startup
catalog = load_product_catalog()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        response = process_message(message, catalog)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vastu', methods=['POST'])
def vastu():
    data = request.json
    room_type = data.get('roomType')
    description = data.get('description')
    
    if not room_type or not description:
        return jsonify({"error": "roomType and description are required"}), 400
    
    try:
        response = process_vastu(room_type, description)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=False)
