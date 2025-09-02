import streamlit as st
from datetime import datetime
from typing import Dict, List

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'processed_docs' not in st.session_state:
        st.session_state.processed_docs = []
    
    if 'current_time' not in st.session_state:
        st.session_state.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def display_chat_message(message: Dict):
    """
    Display a chat message with proper formatting
    
    Args:
        message: Dictionary containing message data
    """
    role = message['role']
    content = message['content']
    timestamp = message.get('timestamp', '')
    
    with st.chat_message(role):
        st.markdown(content)
        
        # Display additional info for assistant messages
        if role == 'assistant':
            # Show route used
            route = message.get('route')
            if route:
                route_icons = {
                    'document': '📄',
                    'web': '🌐', 
                    'hybrid': '🔄'
                }
                st.caption(f"{route_icons.get(route, '🤔')} Route: {route.title()}")
            
            # Show sources in expandable section
            sources = message.get('sources', [])
            if sources:
                with st.expander(f"📚 {len(sources)} Sources", expanded=False):
                    for i, source in enumerate(sources, 1):
                        if source['type'] == 'document':
                            st.markdown(f"**{i}. Document: {source['filename']}** (Page {source.get('page', 'N/A')})")
                            st.markdown(f"*{source['content']}*")
                        else:
                            st.markdown(f"**{i}. Web: {source['title']}**")
                            st.markdown(f"[{source['url']}]({source['url']})")
                            st.markdown(f"*{source['snippet']}*")
                        
                        if i < len(sources):
                            st.markdown("---")
        
        # Show timestamp
        if timestamp:
            st.caption(f"⏰ {timestamp}")

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def validate_environment_variables() -> Dict[str, bool]:
    """
    Validate that required environment variables are set
    
    Returns:
        Dictionary with validation results
    """
    import os
    
    required_vars = {
    'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'SERPER_API_KEY': os.getenv('SERPER_API_KEY')
    }
    
    results = {}
    for var_name, var_value in required_vars.items():
        results[var_name] = bool(var_value and var_value.strip())
    
    return results

def get_file_type_icon(filename: str) -> str:
    """
    Get icon for file type
    
    Args:
        filename: Name of the file
        
    Returns:
        Icon emoji
    """
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    icons = {
        'pdf': '📄',
        'doc': '📝',
        'docx': '📝',
        'txt': '📃',
        'md': '📋'
    }
    
    return icons.get(extension, '📄')

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def estimate_reading_time(text: str) -> str:
    """
    Estimate reading time for text
    
    Args:
        text: Input text
        
    Returns:
        Estimated reading time string
    """
    words = len(text.split())
    minutes = max(1, round(words / 200))  # Average reading speed: 200 words/minute
    
    if minutes == 1:
        return "1 minute"
    else:
        return f"{minutes} minutes"
