import json
import os
from enum import Enum
from typing import List
from llm_client import LLMClient
from agents import ParserAgent, SimilarProductAgent, FAQAgent

class AgentState(Enum):
    INIT = "init"
    PARSE = "parse"
    DESCRIPTION = "description"
    COMPARISON = "comparison"
    FAQ = "faq"
    COMPLETE = "complete"

class GraphNode:
    def __init__(self, name, agent, action):
        self.name = name
        self.agent = agent
        self.action = action
        self.next_nodes = []
        self.status = "PENDING"
    
    def add_next(self, node):
        self.next_nodes.append(node)
    
    def execute(self, state):
        self.status = "RUNNING"
        result = self.action(self.agent, state)
        self.status = "COMPLETED"
        return result
    
    def skip(self):
        self.status = "SKIPPED"

class AgentOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.parser_agent = ParserAgent(self.llm_client)
        self.similar_product_agent = SimilarProductAgent(self.llm_client)
        self.faq_agent = FAQAgent(self.llm_client)
        
        self.templates = self._load_templates()
        self.graph = self._build_graph()
        
    def _load_templates(self):
        templates = {}
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(current_dir, 'templates')
        
        try:
            with open(os.path.join(templates_dir, 'product_description.txt'), 'r') as f:
                templates['description'] = f.read()
        except:
            templates['description'] = "Create a professional product description."
        
        try:
            with open(os.path.join(templates_dir, 'comparison_template.txt'), 'r') as f:
                templates['comparison'] = f.read()
        except:
            templates['comparison'] = "Compare products based on features and price."
        
        try:
            with open(os.path.join(templates_dir, 'faq_template.txt'), 'r') as f:
                templates['faq'] = f.read()
        except:
            templates['faq'] = "Generate comprehensive FAQs."
        
        return templates
    
    def _build_graph(self):
        parse_node = GraphNode(
            "Parse Product Data",
            self.parser_agent,
            lambda agent, state: agent.parse_product(state['input_data'])
        )
        
        description_node = GraphNode(
            "Generate Description",
            self.parser_agent,
            lambda agent, state: agent.generate_description(
                state['parsed_data'], 
                self.templates['description']
            )
        )
        
        comparison_node = GraphNode(
            "Product Comparison",
            self.similar_product_agent,
            self._comparison_action
        )
        
        faq_node = GraphNode(
            "Generate FAQs",
            self.faq_agent,
            lambda agent, state: agent.generate_faqs(
                state['parsed_data'], 
                self.templates['faq']
            )
        )
        
        parse_node.add_next(description_node)
        parse_node.add_next(comparison_node)
        parse_node.add_next(faq_node)
        
        return {
            'parse': parse_node,
            'description': description_node,
            'comparison': comparison_node,
            'faq': faq_node
        }
    
    def _comparison_action(self, agent, state):
        print("Finding similar products in market...")
        similar = agent.find_similar_products(state['parsed_data'])
        print(f"Found {len(similar)} alternative products")
        print("Comparing with your product...")
        comparison = agent.compare_products(
            state['parsed_data'], 
            similar, 
            self.templates['comparison']
        )
        return {'similar_products': similar, 'comparison': comparison}
    
    def run(self, product_data, operations: List[str]):
        for node in self.graph.values():
            node.status = "PENDING"
        
        state = {
            'input_data': product_data,
            'parsed_data': None,
            'description': None,
            'comparison': None,
            'faqs': None
        }
        
        print("\nParser Agent running...")
        parse_node = self.graph['parse']
        state['parsed_data'] = parse_node.execute(state)
        
        results = {'product_data': state['parsed_data']}
        
        if 'description' in operations:
            print("\nDescription Agent running...")
            desc_node = self.graph['description']
            state['description'] = desc_node.execute(state)
            results['description'] = state['description']
        else:
            self.graph['description'].skip()
        
        if 'comparison' in operations:
            print("\nComparison Agent running...")
            comp_node = self.graph['comparison']
            comp_result = comp_node.execute(state)
            state['comparison'] = comp_result
            results['comparison'] = comp_result
        else:
            self.graph['comparison'].skip()
        
        if 'faq' in operations:
            print("\nFAQ Agent running...")
            faq_node = self.graph['faq']
            state['faqs'] = faq_node.execute(state)
            results['faqs'] = state['faqs']
        else:
            self.graph['faq'].skip()
        
        return results
