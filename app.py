"""Flask web server using LangGraph workflow."""
from flask import Flask, request, jsonify, send_file
import json
import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from graph.workflow import run_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def setup_storage() -> None:
    """Create necessary directories for data storage."""
    os.makedirs('data/inputs', exist_ok=True)
    os.makedirs('data/outputs', exist_ok=True)


def save_input(product_data: dict) -> None:
    """Save input data to file.
    
    Args:
        product_data: Product data to save
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if isinstance(product_data, dict):
        name = product_data.get('product_name', 'unknown').replace(' ', '_')
    else:
        name = 'raw_input'
    
    filename = f"input_{name}_{timestamp}.json"
    filepath = os.path.join('data/inputs', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': timestamp, 'product_data': product_data}, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Input saved: {filename}")


def save_output(results: dict, operation: str, product_name: str) -> None:
    """Save output results to file.
    
    Args:
        results: Results to save
        operation: Operation name
        product_name: Product name for filename
    """
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
    
    logger.info(f"Output saved: {filename}")


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_file('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze product using LangGraph workflow.
    
    Request JSON:
        {
            "product_data": <dict or JSON string>,
            "operation": "description|comparison|faq"
        }
    
    Returns:
        JSON with analysis results
    """
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        return jsonify({
            'error': 'GROQ_API_KEY not set. Please set the environment variable.'
        }), 400
    
    try:
        data = request.json
        product_data = data.get('product_data')
        operation = data.get('operation')
        
        if not product_data or not operation:
            return jsonify({'error': 'Missing product_data or operation'}), 400
        
        # Parse JSON if string
        if isinstance(product_data, str):
            try:
                product_data = json.loads(product_data)
            except json.JSONDecodeError:
                # Keep as string if not valid JSON
                pass
        
        # Save input
        save_input(product_data)
        
        # Run workflow
        logger.info(f"Running {operation} operation")
        results = run_workflow(product_data, [operation])
        
        # Save output
        product_name = product_data.get('product_name', 'unknown') if isinstance(product_data, dict) else 'custom_product'
        save_output(results, operation, product_name)
        
        # Add FAQ count info if FAQs generated
        if operation == 'faq' and 'faqs' in results:
            faq_count = len(results.get('faqs', []))
            logger.info(f"Generated {faq_count} FAQs")
            if faq_count < 15:
                logger.warning(f"FAQ count ({faq_count}) is below minimum requirement of 15")
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    setup_storage()
    
    if not os.getenv('GROQ_API_KEY'):
        logger.warning("GROQ_API_KEY not set!")
        logger.warning("Set environment variable: export GROQ_API_KEY='your_key'")
    
    logger.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', debug=False, port=5000)
