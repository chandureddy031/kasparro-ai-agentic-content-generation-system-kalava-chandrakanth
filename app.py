from flask import Flask, request, jsonify, send_file
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

orchestrator = None

def setup_storage():
    os.makedirs('data/inputs', exist_ok=True)
    os.makedirs('data/outputs', exist_ok=True)

def save_input(product_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if isinstance(product_data, dict):
        name = product_data.get('product_name', 'unknown').replace(' ', '_')
    else:
        name = 'raw_input'
    
    filename = f"input_{name}_{timestamp}.json"
    filepath = os.path.join('data/inputs', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': timestamp, 'product_data': product_data}, f, indent=2, ensure_ascii=False)

def save_output(results, operation, product_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = product_name.replace(' ', '_')[:30]
    
    filename = f"output_{operation}_{safe_name}_{timestamp}.json"
    filepath = os.path.join('data/outputs', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'product_name': product_name,
            'operation': operation,
            'results': results
        }, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global orchestrator
    
    if orchestrator is None:
        if not os.getenv('GROQ_API_KEY'):
            return jsonify({
                'error': 'GROQ_API_KEY not set. Please run with: docker run -e GROQ_API_KEY="your_key" -p 5000:5000 your-image'
            }), 400
        
        try:
            from orchestrator import AgentOrchestrator
            orchestrator = AgentOrchestrator()
        except Exception as e:
            return jsonify({'error': f'Failed to initialize: {str(e)}'}), 500
    
    try:
        data = request.json
        product_data = data.get('product_data')
        operation = data.get('operation')
        
        if not product_data or not operation:
            return jsonify({'error': 'Missing data'}), 400
        
        try:
            product_data = json.loads(product_data)
        except:
            pass
        
        save_input(product_data)
        
        results = orchestrator.run(product_data, [operation])
        
        product_name = product_data.get('product_name', 'unknown') if isinstance(product_data, dict) else 'custom_product'
        save_output(results, operation, product_name)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    setup_storage()
    
    if not os.getenv('GROQ_API_KEY'):
        print("WARNING: GROQ_API_KEY not set!")
        print("Run with: docker run -e GROQ_API_KEY='your_key' -p 5000:5000 your-image")
    
    app.run(host='0.0.0.0', debug=False, port=5000)
