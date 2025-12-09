# Project Documentation

## Core Files

### `app.py`
Flask web server that handles HTTP requests and routes them to the orchestrator.
Manages the REST API endpoint `/api/analyze` and serves the frontend HTML file.

### `index.html`
Single-page web interface with embedded CSS and JavaScript for user interaction.
Provides product input form, three action buttons, and dual-mode result display (UI/JSON).

### `Dockerfile`
Container configuration file that packages the entire application with Python 3.11 slim base.
Exposes port 5000 and requires GROQ_API_KEY environment variable at runtime.

### `requirements.txt`
Lists all Python dependencies: Flask 3.0.0, Groq 0.11.0, python-dotenv 1.0.0, werkzeug 3.0.1.
Ensures consistent package versions across development and production environments.

### `docker-compose.yml`
Simplifies Docker deployment by defining service configuration and environment variables.
Allows one-command startup with `GROQ_API_KEY` passed from host environment.

## Source Code (`src/`)

### `src/config.py`
Centralized configuration management for API keys, model settings, and file paths.
Loads environment variables and provides default values for all application settings.

### `src/llm_client.py`
Wrapper class for Groq API that handles JSON generation and text completion requests.
Manages API authentication, error handling, and response parsing from the LLM.

### `src/orchestrator.py`
Graph-based workflow engine that coordinates agent execution in specific order.
Implements node-based routing: Parse → (Description | Comparison | FAQ) based on user selection.

### `src/main.py`
Command-line interface for running the multi-agent system from terminal.
Allows testing and debugging without starting the web server.

## Agents (`src/agents/`)

### `src/agents/parser_agent.py`
Agent 1: Extracts and structures product information from JSON or plain text input.
Generates marketing descriptions using LLM with predefined templates.

### `src/agents/similar_product_agent.py`
Agent 2: Searches for 3 real alternative products from different brands in Indian market.
Creates side-by-side comparison with prices, ratings, features, and differentiators.

### `src/agents/faq_agent.py`
Agent 3: Generates exactly 10 frequently asked questions with detailed answers.
Covers product usage, benefits, safety, results timeline, and storage instructions.

## Templates (`src/templates/`)

### `src/templates/product_description.txt`
Pre-formatted template guiding the LLM to create consistent product descriptions.
Includes sections for title, description, highlights, and usage instructions.

### `src/templates/comparison_template.txt`
Structured format for comparing original product against 3 alternatives.
Ensures uniform presentation of brand, price, rating, features, and differentiators.

### `src/templates/faq_template.txt`
Question-answer template covering 10 standard categories for any product.
Guides LLM to generate comprehensive FAQs about usage, safety, and results.

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

## Workflow Execution Flow

### Parse Node
Entry point that receives raw product data and converts it to structured JSON.
Routes to Description, Comparison, or FAQ node based on user's selected operation.

### Description Node
Generates marketing-ready product description with title, features, and highlights.
Uses Parser Agent with description template to create compelling content.

### Comparison Node
Finds 3 real alternative products using Similar Product Agent.
Creates side-by-side comparison cards with price analysis and differentiators.

### FAQ Node
Generates 10 detailed Q&A pairs covering common product questions.
Uses FAQ Agent with structured template for consistency across products.

## Data Flow

**Input Flow:**
User Input → Frontend → Flask API → Orchestrator → Parse Node → Selected Operation Node → Agent → Groq LLM

**Output Flow:**
Groq LLM → Agent → Node → Orchestrator → Flask API → Frontend (UI/JSON) → Data Storage

## Environment Variables

### `GROQ_API_KEY`
Required API key from Groq Console for accessing llama-3.3-70b-versatile model.
Must be provided via docker run command or .env file for application to function.

### `FLASK_ENV`
Optional setting to switch between development and production modes.
Default is production; set to development for debug logging and auto-reload.

## API Endpoints

### `GET /`
Serves the main index.html page with embedded frontend application.
Returns complete single-page application with all CSS and JavaScript included.

### `POST /api/analyze`
Accepts product data and operation type, returns AI-generated analysis results.
Request body: `{"product_data": "...", "operation": "description|comparison|faq"}`.
