import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import AgentOrchestrator

def setup_storage():
    os.makedirs('data/inputs', exist_ok=True)
    os.makedirs('data/outputs', exist_ok=True)

def load_sample_data():
    try:
        with open('data/sample_product.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
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

def get_user_input():
    print("\nPaste your product data (JSON or text). Type DONE when finished:\n")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'DONE':
                break
            lines.append(line)
        except EOFError:
            break
    
    text = "\n".join(lines).strip()
    if not text:
        return load_sample_data()
    
    try:
        return json.loads(text)
    except:
        return text

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
    
    print(f"\nInput saved: {filename}")

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
    
    print(f"Output saved: {filename}")

def main():
    setup_storage()
    
    print("\n" + "="*60)
    print("MULTI-AGENT PRODUCT ANALYSIS SYSTEM")
    print("="*60)
    
    orchestrator = AgentOrchestrator()
    
    print("\n1. User Input")
    print("2. Sample Input")
    choice = input("\nSelect (1-2): ").strip()
    
    if choice == '2':
        product_data = load_sample_data()
        print(f"\nUsing sample: {product_data.get('product_name')}")
        save_input(product_data)
        
        print("\nRunning all 3 agents...")
        
        results_desc = orchestrator.run(product_data, ['description'])
        product_name = product_data.get('product_name', 'unknown')
        save_output(results_desc, 'description', product_name)
        print(json.dumps(results_desc, indent=2, ensure_ascii=False))
        
        results_comp = orchestrator.run(product_data, ['comparison'])
        save_output(results_comp, 'comparison', product_name)
        print(json.dumps(results_comp, indent=2, ensure_ascii=False))
        
        results_faq = orchestrator.run(product_data, ['faq'])
        save_output(results_faq, 'faq', product_name)
        print(json.dumps(results_faq, indent=2, ensure_ascii=False))
        
        print("\nAll operations completed.")
    
    else:
        product_data = get_user_input()
        save_input(product_data)
        
        while True:
            print("\n" + "="*60)
            print("SELECT AGENT")
            print("="*60)
            print("1. Product Description")
            print("2. Product Comparison")
            print("3. Generate FAQs")
            print("4. Exit")
            
            agent_choice = input("\nSelect (1-4): ").strip()
            
            if agent_choice == '4':
                break
            
            operation_map = {
                '1': 'description',
                '2': 'comparison',
                '3': 'faq'
            }
            
            operation = operation_map.get(agent_choice)
            if not operation:
                continue
            
            print(f"\nRunning {operation}...")
            results = orchestrator.run(product_data, [operation])
            
            product_name = product_data.get('product_name', 'unknown') if isinstance(product_data, dict) else 'custom_product'
            save_output(results, operation, product_name)
            
            print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
