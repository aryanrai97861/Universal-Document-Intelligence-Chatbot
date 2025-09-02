import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()
from pathlib import Path
from components.document_processor import DocumentProcessor
from components.vector_store import VectorStore
from components.query_router import QueryRouter
from components.web_search import WebSearch
from components.llm_handler import LLMHandler
from utils.helpers import initialize_session_state, display_chat_message

# Page configuration
st.set_page_config(
    page_title="Universal Document Intelligence Chatbot",
    page_icon="🧠",
    layout="wide"
)

def main():
    st.title("🧠 Universal Document Intelligence Chatbot")
    st.markdown("Upload documents and ask questions. I'll search your documents or the web as needed!")
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize components
    if 'components_initialized' not in st.session_state:
            try:
                st.session_state.doc_processor = DocumentProcessor()
                st.session_state.vector_store = VectorStore()
                st.session_state.query_router = QueryRouter()
                # WebSearch may require an API key; initialize safely
                try:
                    st.session_state.web_search = WebSearch()
                    st.session_state.web_search_available = True
                except Exception:
                    st.session_state.web_search = None
                    st.session_state.web_search_available = False

                st.session_state.llm_handler = LLMHandler()
                st.session_state.components_initialized = True
            except Exception as e:
                st.error(f"Failed to initialize components: {str(e)}")
                st.stop()
    
    # Sidebar for document management
    with st.sidebar:
        st.header("📄 Document Management")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload PDF files to create your knowledge base"
        )
        
        if uploaded_files:
            if st.button("Process Documents", type="primary"):
                process_documents(uploaded_files)
        
        # Display processed documents
        if st.session_state.processed_docs:
            st.subheader("📚 Processed Documents")
            for doc_info in st.session_state.processed_docs:
                st.write(f"📄 {doc_info['filename']} ({doc_info['chunks']} chunks)")
        
        # Clear documents
        if st.session_state.processed_docs:
            if st.button("🗑️ Clear All Documents"):
                clear_documents()
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            display_chat_message(message)
    
    # Chat input
    user_input = st.chat_input("Ask a question about your documents or anything else...")
    
    if user_input:
        handle_user_query(user_input)

def process_documents(uploaded_files):
    """Process uploaded documents and add to vector store"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process document
            chunks = st.session_state.doc_processor.process_pdf(temp_path, uploaded_file.name)
            
            # Add to vector store
            st.session_state.vector_store.add_documents(chunks)
            
            # Track processed document
            st.session_state.processed_docs.append({
                'filename': uploaded_file.name,
                'chunks': len(chunks)
            })
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("✅ All documents processed successfully!")
        st.success(f"Processed {len(uploaded_files)} documents with {sum(doc['chunks'] for doc in st.session_state.processed_docs)} total chunks")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()

def clear_documents():
    """Clear all processed documents and vector store"""
    try:
        st.session_state.vector_store.clear()
        st.session_state.processed_docs = []
        st.success("All documents cleared!")
        st.rerun()
    except Exception as e:
        st.error(f"Error clearing documents: {str(e)}")

def handle_user_query(user_input):
    """Handle user query with routing logic"""
    # Add user message to chat history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': st.session_state.get('current_time', '')
    })
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Route the query
                route_decision = st.session_state.query_router.route_query(
                    user_input, 
                    has_documents=len(st.session_state.processed_docs) > 0
                )
                
                response_data = None
                
                if route_decision['route'] == 'document':
                    # Search in documents
                    relevant_docs = st.session_state.vector_store.search(user_input, k=3)
                    if relevant_docs:
                        response_data = st.session_state.llm_handler.generate_document_response(
                            user_input, relevant_docs
                        )
                    else:
                        # No relevant documents found, fallback to web search if available
                        if st.session_state.get('web_search_available') and st.session_state.web_search is not None:
                            web_results = st.session_state.web_search.search(user_input)
                            response_data = st.session_state.llm_handler.generate_web_response(
                                user_input, web_results
                            )
                        else:
                            response_data = {
                                'response': "I couldn't find relevant information in your documents and web search is not available. Please upload more documents or enable SERPER_API_KEY for web search.",
                                'sources': []
                            }
                        
                elif route_decision['route'] == 'web':
                    # Search on web (if available)
                    if st.session_state.get('web_search_available') and st.session_state.web_search is not None:
                        web_results = st.session_state.web_search.search(user_input)
                        response_data = st.session_state.llm_handler.generate_web_response(
                            user_input, web_results
                        )
                    else:
                        response_data = {
                            'response': "Web search is currently unavailable (SERPER_API_KEY not set). Please enable it in your environment to allow web-based answers.",
                            'sources': []
                        }
                    
                else:
                    # Hybrid approach
                    relevant_docs = st.session_state.vector_store.search(user_input, k=2)
                    if st.session_state.get('web_search_available') and st.session_state.web_search is not None:
                        web_results = st.session_state.web_search.search(user_input)
                    else:
                        web_results = []
                    response_data = st.session_state.llm_handler.generate_hybrid_response(
                        user_input, relevant_docs, web_results
                    )
                
                # Display response
                if response_data:
                    st.markdown(response_data['response'])
                    
                    # Display sources
                    if response_data.get('sources'):
                        with st.expander("📚 Sources", expanded=False):
                            for i, source in enumerate(response_data['sources'], 1):
                                if source['type'] == 'document':
                                    st.markdown(f"**{i}. Document: {source['filename']}** (Page {source.get('page', 'N/A')})")
                                    st.markdown(f"*{source['content'][:200]}...*")
                                else:
                                    st.markdown(f"**{i}. Web: {source['title']}**")
                                    st.markdown(f"[{source['url']}]({source['url']})")
                                    st.markdown(f"*{source['snippet'][:200]}...*")
                                st.markdown("---")
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response_data['response'],
                        'sources': response_data.get('sources', []),
                        'route': route_decision['route'],
                        'timestamp': st.session_state.get('current_time', '')
                    })
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'timestamp': st.session_state.get('current_time', '')
                })
    
    st.rerun()

if __name__ == "__main__":
    main()
