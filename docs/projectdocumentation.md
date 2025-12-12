# Project Documentation

## Architecture Overview

### LangGraph-Based Multi-Agent System

This system uses **LangGraph** (from LangChain) to orchestrate multiple specialized agents in a stateful workflow. The architecture follows industry best practices by leveraging established frameworks rather than custom implementations.

**Key Design Decisions:**
- **StateGraph**: Uses LangGraph's `StateGraph` as the orchestration mechanism
- **Typed State**: Implements `AgentState` TypedDict for type-safe state management
- **Pydantic Models**: All outputs are validated using Pydantic schemas
- **Structured Output**: Uses schema-based generation instead of prompt engineering
- **Retry Logic**: Implements exponential backoff for LLM API calls

### Workflow State Flow

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Parser Node    │ ← Extracts & validates product data
│  (Always Runs)  │
└──────┬──────────┘
       │
       ├──────────► [Conditional Routing]
       │
       ▼
┌─────────────────┐
│ Description     │ ← Generates marketing description
│ (Optional)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Comparison      │ ← Finds & compares similar products
│ (Optional)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  FAQ Node       │ ← Generates minimum 15 categorized FAQs
│  (Optional)     │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│    END      │
└─────────────┘
```

**State Transitions:**
1. All workflows start with the **Parser Node** (mandatory)
2. Conditional edges route to requested operations in order:
   - If 'description' requested → Description Node
   - If 'comparison' requested → Comparison Node  
   - If 'faq' requested → FAQ Node
3. Each node modifies the shared `AgentState`
4. Workflow ends when all requested operations complete

### Agent Responsibilities

Each agent is implemented as a LangGraph **node function** that:
1. Receives the current `AgentState`
2. Performs its specialized task
3. Updates specific state fields
4. Returns the modified state

#### Parser Node (`src/graph/nodes.py::parser_node`)
- **Input**: Raw product data (dict or text)
- **Output**: `ParsedProduct` Pydantic model
- **State Field**: `parsed_data`
- **Purpose**: Structure and validate product information

#### Description Node (`src/graph/nodes.py::description_node`)
- **Input**: `parsed_data` from state
- **Output**: `ProductDescription` Pydantic model
- **State Field**: `description`
- **Purpose**: Generate marketing copy using templates

#### Comparison Node (`src/graph/nodes.py::comparison_node`)
- **Input**: `parsed_data` from state
- **Output**: `ProductComparison` with 3 similar products
- **State Field**: `comparison`, `similar_products`
- **Purpose**: Find alternatives and generate comparison analysis

#### FAQ Node (`src/graph/nodes.py::faq_node`)
- **Input**: `parsed_data` from state
- **Output**: `FAQPage` with minimum 15 FAQs
- **State Field**: `faqs`
- **Purpose**: Generate categorized FAQs (Informational, Safety, Usage, Purchase, Comparison)
- **Validation**: Pydantic enforces min_length=15 constraint

## Core Files

### `src/graph/workflow.py`
**LangGraph StateGraph** definition that replaces the old custom orchestrator.
- Defines the workflow structure using LangGraph primitives
- Implements conditional routing functions
- Compiles the graph into an executable workflow
- Provides `run_workflow()` function for execution

### `src/graph/nodes.py`
Node functions for each agent that transform the `AgentState`.
- Each function takes `AgentState` and returns modified `AgentState`
- Uses `LLMClient.generate_structured()` for type-safe outputs
- Includes fallback logic for robustness

### `src/models/state.py`
TypedDict definition for the shared state passed between nodes.
- Defines all possible state fields with types
- Used by LangGraph to track workflow state

### `src/models/outputs.py`
Pydantic models for all agent outputs with validation:
- `ParsedProduct`: Structured product data
- `ProductDescription`: Marketing description
- `FAQ`: Single FAQ with category
- `FAQPage`: Container for minimum 15 FAQs (enforced by Pydantic)
- `ProductComparison`: Comparison analysis structure

### `src/llm_client.py`
Enhanced LLM client with structured output support:
- `generate()`: Basic text generation with retry logic
- `generate_structured()`: Schema-based generation using Pydantic models
- Includes retry decorator with exponential backoff
- Proper error handling and logging

### `src/config.py`
Configuration management with environment variable support:
- `MODEL_NAME`: Configurable via `MODEL_NAME` env var (default: llama-3.3-70b-versatile)
- `TEMPERATURE`: Configurable via `TEMPERATURE` env var (default: 0.7)
- `MAX_TOKENS`: Configurable via `MAX_TOKENS` env var (default: 2048)
- `GROQ_API_KEY`: Required environment variable

### `src/main.py`
CLI entry point with argument parsing (no interactive prompts):
- `--input`: Path to JSON file with product data
- `--operations`: Comma-separated list (description,comparison,faq)
- `--sample`: Use built-in sample data
- `--output-dir`: Custom output directory

### `app.py`
Flask web server (legacy - uses old orchestrator).
**Note**: This file still uses the old custom orchestrator and should be updated separately.

## Agents (`src/agents/`)

**Note**: These files are legacy implementations. The new system uses node functions in `src/graph/nodes.py` instead of agent classes.

### `src/agents/parser_agent.py`
**Legacy**: Agent class for parsing. New system uses `parser_node()` in `src/graph/nodes.py`.

### `src/agents/similar_product_agent.py`
**Legacy**: Agent class for comparison. New system uses `comparison_node()` in `src/graph/nodes.py`.

### `src/agents/faq_agent.py`
**Legacy**: Agent class that generated 10 FAQs. New system uses `faq_node()` which generates **minimum 15 FAQs** with categories.

## Templates (`src/templates/`)

### `src/templates/product_description.txt`
Pre-formatted template guiding the LLM to create consistent product descriptions.
Includes sections for title, description, highlights, and usage instructions.

### `src/templates/comparison_template.txt`
Structured format for comparing original product against 3 alternatives.
Ensures uniform presentation of brand, price, rating, features, and differentiators.

### `src/templates/faq_template.txt`
**Updated**: Now requests **minimum 15 FAQs** with required categorization:
- Informational (3+ questions)
- Safety (3+ questions)
- Usage (3+ questions)
- Purchase (3+ questions)
- Comparison (3+ questions)

## Data Storage (`data/`)

### `data/inputs/`
Stores all user-submitted product data with timestamp-based JSON filenames.
Preserves original input for audit trail and reprocessing capabilities.

### `data/outputs/`
Saves all generated results (descriptions, comparisons, FAQs) as timestamped JSON files.
Enables result retrieval, analysis, and performance tracking over time.

### `data/history/`
Maintains execution logs with timestamps, operations performed, and agent activity.
Useful for debugging, monitoring system performance, and usage analytics.

### `data/sample_product.json`
Example product data demonstrating the expected JSON schema format.
Helps users understand required and optional fields for input.

## CI/CD (`.github/workflows/`)

### `.github/workflows/ci-cd.yml`
Automated pipeline that runs tests on every push and pull request to main branch.
Validates dependencies, checks code structure, and pulls Docker image for testing.

## Workflow Execution Flow (LangGraph)

### Parse Node (Always Runs)
Entry point that receives raw product data and validates it using `ParsedProduct` Pydantic model.
Creates structured state that subsequent nodes depend on.

### Description Node (Conditional)
Generates marketing-ready product description with title, features, and highlights.
Uses `ProductDescription` Pydantic model to ensure consistent structure.
Only runs if 'description' is in the operations list.

### Comparison Node (Conditional)
Finds 3 real alternative products and generates detailed comparison analysis.
Validates output with `ProductComparison` and `SimilarProduct` Pydantic models.
Only runs if 'comparison' is in the operations list.

### FAQ Node (Conditional)
Generates **minimum 15 categorized FAQs** with Pydantic validation.
Uses `FAQPage` model which enforces `min_length=15` constraint.
Only runs if 'faq' is in the operations list.

**Key Improvement**: Pydantic validation ensures the system cannot return fewer than 15 FAQs.

## Data Flow (LangGraph Architecture)

**Input Flow:**
CLI/API → `run_workflow()` → StateGraph Entry Point → Parser Node → State Update → Conditional Routing → Selected Nodes → State Updates → Final State

**State Management:**
Each node receives `AgentState`, modifies relevant fields, and returns updated state.
LangGraph automatically manages state propagation between nodes.

**Output Flow:**
Final State → Result Extraction → JSON Response → File Storage

## Testing

### `tests/test_models.py`
Unit tests for Pydantic models:
- Validates FAQ minimum count constraint (15+)
- Tests all model schemas
- Ensures proper validation errors

### `tests/test_workflow.py`
Integration tests for LangGraph workflow:
- Validates workflow compilation
- Tests conditional routing logic
- Ensures state transitions work correctly

## Environment Variables

### `GROQ_API_KEY` (Required)
Required API key from Groq Console for accessing LLM models.
Must be provided via environment variable or .env file.

### `MODEL_NAME` (Optional)
LLM model to use. Default: `llama-3.3-70b-versatile`
Can be overridden to use different Groq models.

### `TEMPERATURE` (Optional)
Sampling temperature for LLM generation. Default: `0.7`
Range: 0.0 (deterministic) to 2.0 (creative)

### `MAX_TOKENS` (Optional)
Maximum tokens in LLM responses. Default: `2048`
Increase for longer outputs (e.g., 4096 for FAQs)

## API Endpoints

### `GET /`
Serves the main index.html page with embedded frontend application.
Returns complete single-page application with all CSS and JavaScript included.

### `POST /api/analyze`
Accepts product data and operation type, returns AI-generated analysis results.
Request body: `{"product_data": "...", "operation": "description|comparison|faq"}`.
