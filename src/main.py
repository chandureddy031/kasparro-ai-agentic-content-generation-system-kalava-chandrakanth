"""Main entry point for the multi-agent system using LangGraph.

This module provides a CLI interface to run the workflow.
"""
import json
import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.workflow import run_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_storage() -> None:
    """Create necessary directories for data storage."""
    os.makedirs('data/inputs', exist_ok=True)
    os.makedirs('data/outputs', exist_ok=True)


def load_sample_data() -> dict:
    """Load sample product data.
    
    Returns:
        Sample product dictionary
    """
    try:
        with open('data/sample_product.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load sample data: {e}")
        return {
            "product_name": "GlowBoost Vitamin C Serum",
            "concentration": "10% Vitamin C",
            "skin_type": "Oily, Combination",
            "key_ingredients": "Vitamin C, Hyaluronic Acid",
            "benefits": "Brightening, Fades dark spots",
            "how_to_use": "Apply 2-3 drops in the morning before sunscreen",
            "side_effects": "Mild tingling for sensitive skin",
            "price": "₹699"
        }


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


def load_product_from_file(filepath: str) -> dict:
    """Load product data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Product data dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle both raw dict and wrapped format
        if 'product_data' in data:
            return data['product_data']
        return data


def main() -> None:
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Multi-Agent Product Analysis System using LangGraph'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to input JSON file with product data'
    )
    parser.add_argument(
        '--operations',
        type=str,
        default='description,comparison,faq',
        help='Comma-separated operations: description,comparison,faq (default: all)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Use sample product data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/outputs',
        help='Output directory (default: data/outputs)'
    )
    
    args = parser.parse_args()
    
    setup_storage()
    
    print("\n" + "="*60)
    print("MULTI-AGENT PRODUCT ANALYSIS SYSTEM (LangGraph)")
    print("="*60)
    
    # Load product data
    if args.sample or not args.input:
        print("\nUsing sample product data...")
        product_data = load_sample_data()
    else:
        print(f"\nLoading product data from: {args.input}")
        try:
            product_data = load_product_from_file(args.input)
        except Exception as e:
            logger.error(f"Failed to load input file: {e}")
            sys.exit(1)
    
    # Parse operations
    operations = [op.strip() for op in args.operations.split(',')]
    valid_operations = ['description', 'comparison', 'faq']
    operations = [op for op in operations if op in valid_operations]
    
    if not operations:
        logger.error("No valid operations specified. Use: description, comparison, faq")
        sys.exit(1)
    
    print(f"\nProduct: {product_data.get('product_name', 'Unknown')}")
    print(f"Operations: {', '.join(operations)}")
    
    # Save input
    save_input(product_data)
    
    # Run workflow
    print("\n" + "-"*60)
    print("Running LangGraph workflow...")
    print("-"*60 + "\n")
    
    try:
        results = run_workflow(product_data, operations)
        
        # Display results
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60 + "\n")
        
        if 'error' in results:
            print(f"⚠️  Warning: {results['error']}\n")
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # Save outputs
        product_name = product_data.get('product_name', 'unknown')
        
        if 'description' in operations and 'description' in results:
            save_output({'description': results['description']}, 'description', product_name)
        
        if 'comparison' in operations and 'comparison' in results:
            save_output({'comparison': results['comparison']}, 'comparison', product_name)
        
        if 'faq' in operations and 'faqs' in results:
            faq_count = len(results.get('faqs', []))
            print(f"\n✅ Generated {faq_count} FAQs (minimum 15 required)")
            if faq_count < 15:
                print("⚠️  WARNING: FAQ count is below minimum requirement!")
            save_output({'faqs': results['faqs']}, 'faq', product_name)
        
        print("\n" + "="*60)
        print("COMPLETED")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
