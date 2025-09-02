# Universal Document Intelligence Chatbot

## Overview

This is a comprehensive document intelligence chatbot built with Streamlit that provides intelligent query routing between uploaded documents and web search. The system can process PDF documents, create semantic embeddings for efficient retrieval, and automatically determine whether to search within uploaded documents or fetch information from the web based on query analysis. It combines document processing, vector search, web search, and LLM capabilities to create a universal knowledge assistant.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with chat interface
- **Layout**: Wide layout with sidebar for document management and main area for chat
- **Session Management**: Streamlit session state for maintaining chat history, processed documents, and component instances
- **File Upload**: Multi-file PDF upload support with real-time processing feedback

### Backend Architecture
- **Modular Component Design**: Separated into distinct components for document processing, vector storage, query routing, web search, and LLM handling
- **Document Processing**: PyPDF2-based PDF text extraction with intelligent chunking that preserves document structure and metadata
- **Query Routing Logic**: Rule-based system that analyzes queries for temporal keywords, explanatory terms, comparisons, and current data requests to determine optimal search strategy
- **Vector Search**: Semantic similarity search using ChromaDB with OpenAI embeddings for document retrieval
- **LLM Integration**: Gemini 2.5 Flash model for generating contextual responses from both document and web sources

### Data Storage Solutions
- **Vector Database**: ChromaDB persistent storage for document embeddings with cosine similarity search
- **Embedding Model**: OpenAI text-embedding-3-small for converting text to vector representations
- **Document Chunking**: Configurable chunk size (1000 characters) with overlap (200 characters) for optimal retrieval
- **Metadata Preservation**: Maintains filename, page numbers, and document structure information

### Authentication and Authorization
- **API Key Management**: Environment variable-based configuration for external service credentials
- **Required Keys**: GEMINI_API_KEY, OPENAI_API_KEY, SERPER_API_KEY
- **No User Authentication**: Single-user application design without login requirements

## External Dependencies

### AI and ML Services
- **Google Gemini 2.5 Flash**: Primary LLM for response generation and reasoning
- **OpenAI Embeddings API**: Text embedding generation for semantic search
- **Sentence Transformers**: Alternative embedding option mentioned in documentation

### Search and Data Sources
- **Serper.dev API**: Web search capabilities with Google search results
- **Web Search Integration**: RESTful API calls with configurable result limits and geographic targeting

### Core Libraries and Frameworks
- **Streamlit**: Web application framework for the user interface
- **ChromaDB**: Vector database for persistent embedding storage
- **PyPDF2**: PDF document parsing and text extraction
- **Requests**: HTTP client for web search API calls
- **Python-dotenv**: Environment variable management
- **LangChain**: Referenced for potential advanced document processing capabilities

### Development and Deployment
- **Python 3.8+**: Runtime environment requirement
- **Pip**: Package management for dependency installation
- **Local File System**: Document storage and ChromaDB persistence