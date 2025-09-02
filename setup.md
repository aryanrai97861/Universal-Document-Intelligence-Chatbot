# Universal Document Intelligence Chatbot Setup Guide

This guide will help you set up and run the Universal Document Intelligence Chatbot application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Quick Start

1. Install dependencies: `pip install streamlit chromadb openai google-genai PyPDF2 requests python-dotenv`
2. Copy `.env.example` to `.env` and add your API keys
3. Run: `streamlit run app.py --server.port 5000`
4. Open http://localhost:5000 in your browser

## Detailed Installation Steps

### 1. Install Required Packages

Run the following command to install all required Python packages:

```bash
pip install streamlit chromadb openai google-genai PyPDF2 requests python-dotenv
```

### 2. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Then edit the `.env` file and add your actual API keys:

```bash
# OpenAI API Key for document embeddings
OPENAI_API_KEY=your_actual_openai_key_here

# Google Gemini API Key for AI responses
GEMINI_API_KEY=your_actual_gemini_key_here

# Serper.dev API Key for web search (optional)
SERPER_API_KEY=your_actual_serper_key_here
```

### 3. Create Streamlit Configuration

Create the Streamlit configuration directory and file:

```bash
mkdir -p .streamlit
```

The configuration should already exist in `.streamlit/config.toml` with these settings:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## API Keys Setup Guide

### Required API Keys

#### 1. OpenAI API Key
- **Purpose**: Used for generating document embeddings for semantic search
- **Get it from**: https://platform.openai.com/api-keys
- **Steps**:
  1. Create an OpenAI account
  2. Go to API Keys section
  3. Create new secret key
  4. Copy the key (starts with `sk-`)

#### 2. Google Gemini API Key
- **Purpose**: Used for generating intelligent responses and reasoning
- **Get it from**: https://aistudio.google.com/app/apikey
- **Steps**:
  1. Go to Google AI Studio
  2. Sign in with Google account
  3. Create new API key
  4. Copy the key

#### 3. Serper.dev API Key (Optional)
- **Purpose**: Used for web search functionality when documents don't contain the answer
- **Get it from**: https://serper.dev/dashboard
- **Steps**:
  1. Create account on Serper.dev
  2. Go to dashboard
  3. Copy your API key
- **Note**: If not provided, web search features will be disabled

## Running the Application

### Start the Application

```bash
streamlit run app.py --server.port 5000
```

### Access the Application

Open your browser and go to:
- Local: http://localhost:5000
- Network: http://0.0.0.0:5000

## Usage Guide

### 1. Upload Documents
- Click "Browse files" in the sidebar
- Select one or more PDF files
- Click "Process Documents" to analyze and index them

### 2. Chat with Your Documents
- Type questions in the chat input at the bottom
- The system will automatically decide whether to:
  - Search your uploaded documents
  - Search the web
  - Use both sources for comprehensive answers

### 3. Query Types

#### Document Search Examples:
- "What does the contract say about payment terms?"
- "Summarize the main points from the uploaded report"
- "According to the document, what are the requirements?"

#### Web Search Examples:
- "What's the latest news about AI?"
- "How does machine learning work?"
- "Compare Python vs JavaScript in 2024"

#### Hybrid Search Examples:
- "How does this document compare to current industry standards?"
- "What are the latest updates on the topic mentioned in my document?"

## Features

### ✅ Core Functionality
- **Multi-PDF Support**: Upload and process multiple PDF documents
- **Intelligent Chunking**: Smart text splitting that preserves context
- **Semantic Search**: Vector-based document search using embeddings
- **Smart Query Routing**: Automatic decision between document/web/hybrid search
- **Chat Interface**: Interactive conversation with your documents
- **Source Citations**: Clear references to document pages or web sources

### ✅ Smart Routing Logic
The system automatically routes queries based on:
- **Document Mode**: Questions about uploaded content
- **Web Mode**: Current events, definitions, comparisons
- **Hybrid Mode**: Questions requiring both sources

## Troubleshooting

### Common Issues

1. **"API Key Error"**
   - Ensure all required API keys are set in `.env` file
   - Verify keys are valid and not expired
   - Check for extra spaces or characters

2. **"No documents processed"**
   - Ensure PDFs are not password-protected
   - Check file size limits
   - Verify PDF contains extractable text

3. **"ChromaDB errors"**
   - Delete the `chroma_db` folder and restart
   - Ensure write permissions in the directory

4. **"Port already in use"**
   - Change port in command: `streamlit run app.py --server.port 5001`
   - Kill existing processes using the port

### Performance Tips

- **Large Documents**: Consider splitting very large PDFs into smaller files
- **Many Documents**: Processing time increases with document count
- **Embeddings**: First-time processing takes longer due to embedding generation

## Directory Structure

```
.
├── app.py                 # Main Streamlit application
├── components/            # Core functionality modules
│   ├── document_processor.py    # PDF processing and chunking
│   ├── vector_store.py          # ChromaDB vector storage
│   ├── query_router.py          # Intelligent query routing
│   ├── web_search.py            # Web search functionality
│   └── llm_handler.py           # LLM response generation
├── utils/                 # Helper utilities
│   └── helpers.py              # UI and utility functions
├── .streamlit/           # Streamlit configuration
│   └── config.toml            # Server configuration
├── chroma_db/            # Vector database storage (auto-created)
├── .env                  # Environment variables (you create this)
├── .env.example         # Environment template
└── setup.md             # This setup guide
```

## Security Notes

- Never commit `.env` file to version control
- Keep API keys secure and don't share them
- Use environment variables for all sensitive data
- Regularly rotate API keys for security

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all API keys are correctly configured
3. Ensure all dependencies are installed
4. Check the console/terminal for error messages
