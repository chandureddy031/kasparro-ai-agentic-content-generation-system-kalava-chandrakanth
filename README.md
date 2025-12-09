# 🤖 Multi-Agent Product Analysis System

A powerful AI-driven product analysis platform using multi-agent architecture with LangGraph-style orchestration and Groq LLM integration.

![System Architecture](img-kasparrow.png)

## 📸 Application Preview

![Application Screenshot](Screenshot%202025-12-09%20133520.png)

## 🌟 Features

- **Multi-Agent Architecture**: Three specialized agents working in orchestrated workflow
  - **Parser Agent**: Extracts and structures product data
  - **Similar Product Agent**: Finds and compares market alternatives
  - **FAQ Agent**: Generates 10 detailed frequently asked questions

- **Graph-Based Orchestration**: LangGraph-inspired node execution with dynamic routing

- **Dual Output Modes**: 
  - Beautiful UI with side-by-side comparison cards
  - JSON output for technical inspection

- **Real-time Analysis**: Uses Groq's latest LLM (llama-3.3-70b-versatile) for accurate results

- **Data Persistence**: Automatic storage of inputs, outputs, and execution history

## 🏗️ System Architecture


## 🚀 Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Groq API Key ([Get it here](#getting-groq-api-key))

### Pull and Run


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

