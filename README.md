# 🤖 Multi-Agent Product Analysis System (LangGraph)


    Running application : https://product-analysis-app-latest.onrender.com




A powerful AI-driven product analysis platform using **LangGraph** for orchestration and Groq LLM integration.

![System Architecture](img-kasparrow.png)

## 📸 Application Preview

![Application Screenshot](Screenshot%202025-12-09%20133520.png)

## 🌟 Features

- **LangGraph-Based Architecture**: Industry-standard orchestration using StateGraph
  - **Parser Node**: Extracts and validates product data with Pydantic
  - **Comparison Node**: Finds and compares 3 market alternatives
  - **FAQ Node**: Generates **minimum 15 categorized FAQs** (enforced by schema)
  - **Description Node**: Creates marketing-ready product descriptions

- **Structured Output**: Pydantic models ensure type-safe, validated outputs

- **Robust Error Handling**: 
  - Exponential backoff retry logic for API calls
  - Proper logging instead of silent failures
  - Fallback mechanisms for critical operations

- **Configurable**: Environment variables for model selection, temperature, and tokens

- **15+ FAQs with Categories**: 
  - Informational (3+)
  - Safety (3+)
  - Usage (3+)
  - Purchase (3+)
  - Comparison (3+)

## 🏗️ LangGraph Architecture

```
Entry → Parser Node (Always)
         ↓
         ├→ Description Node (Optional)
         ├→ Comparison Node (Optional)
         └→ FAQ Node (Optional - Min 15 FAQs)
         ↓
         End
```

**Key Components:**
- `StateGraph`: Orchestrates agent execution
- `AgentState`: TypedDict for type-safe state management
- Conditional routing based on requested operations
- Pydantic validation at every step

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ or Docker
- Groq API Key ([Get it here](#getting-groq-api-key))

### Using CLI (Recommended)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GROQ_API_KEY='your_api_key_here'
```

3. Run with sample data:
```bash
cd src
python main.py --sample --operations=faq
```

4. Run with custom data:
```bash
python main.py --input=/path/to/product.json --operations=description,comparison,faq
```

### Using Docker

```bash
docker build -t product-analysis .
docker run -e GROQ_API_KEY='your_key' -p 5000:5000 product-analysis
```

### Access the Application

Open your browser and navigate to:
http://localhost:5000


## 🔑 Getting Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy your key (format: `gsk_...`)
6. Use it in the docker run command

## 💻 Local Development Setup

### 1. Clone the Repository


git clone https://github.com/yourusername/product-analysis-app.git
cd product-analysis-app### 2. Install Dependencies

pip install -r requirements.txt


### 3. Set Environment Variable

**Linux/Mac:**
export GROQ_API_KEY="your_groq_api_key_here"


## 🎯 Usage

### 1. Input Your Product Data

Enter product information in JSON format or plain text:

**JSON Format:**


## 🚢 CI/CD Pipeline

This project includes GitHub Actions workflow for automated testing and deployment.

Triggers on: push to main/master, pull requests

Actions: Install dependencies, run tests, pull Docker image

## 🛠️ Tech Stack

- **Backend**: Python 3.10+
- **Orchestration**: **LangGraph** (official LangChain framework)
- **LLM**: Groq (llama-3.3-70b-versatile, configurable)
- **Validation**: Pydantic 2.x for structured outputs
- **Web Server**: Flask (optional - CLI is primary interface)
- **Retry Logic**: Tenacity for exponential backoff
- **Containerization**: Docker

## 📋 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | None | Groq API key for LLM access |
| `MODEL_NAME` | No | `llama-3.3-70b-versatile` | Groq model to use |
| `TEMPERATURE` | No | `0.7` | LLM sampling temperature |
| `MAX_TOKENS` | No | `2048` | Maximum tokens per response |

## 🧪 Testing

Run the included tests to validate the system:

```bash
# Test Pydantic models
python tests/test_models.py

# Test LangGraph workflow
python tests/test_workflow.py
```

**Key Tests:**
- ✅ FAQPage enforces minimum 15 FAQs
- ✅ Workflow compilation succeeds
- ✅ Conditional routing works correctly
- ✅ All Pydantic models validate properly

## 📊 Output Examples

### FAQ Output (15+ with Categories)
```json
{
  "faqs": [
    {
      "question": "What is this product?",
      "answer": "Detailed answer...",
      "category": "Informational"
    },
    // ... minimum 15 total
  ]
}
```

### Validation Guarantee
The system **cannot** return fewer than 15 FAQs due to Pydantic's `min_length=15` constraint on the `FAQPage` model.
- **CI/CD**: GitHub Actions

## 📝 API Endpoints

### POST `/api/analyze`

Analyzes product data using specified operation.

**Request:**

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Chandu**
- Docker Hub: [chandu013](https://hub.docker.com/u/chandu013)

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for lightning-fast LLM inference
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration inspiration

## 📞 Support

For issues and questions, open an Issue on GitHub

## 🔄 Version History

- **v1.0.0** (December 2025)
  - Initial release
  - Multi-agent architecture
  - Docker support
  - CI/CD pipeline

---

⭐ **Star this repository if you find it helpful!**

Made with ❤️ using AI-powered multi-agent systems

## 🚀 Run with Docker

### 1️⃣ Pull the Image
```bash
docker pull chandu013/product-analysis-app:latest
GROQ_API_KEY=your_groq_api_key_here
docker run -it --env-file .env -p 5000:5000 chandu013/product-analysis-app
http://localhost:5000

That’s it. ✅  
If you want a **full README** or **Docker Hub README version**, tell me.


