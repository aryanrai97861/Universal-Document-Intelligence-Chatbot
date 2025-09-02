import os
from typing import List, Dict, Optional
from google import genai
from google.genai import types

class LLMHandler:
    """Handles LLM interactions using Gemini 2.5 Flash"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or not api_key.strip():
            raise ValueError("GEMINI_API_KEY environment variable is required. Please set GEMINI_API_KEY in your environment or .env file.")

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google GenAI client: {e}")

        self.model = "gemini-2.5-flash"
    
    def generate_document_response(self, query: str, relevant_docs: List[Dict]) -> Dict:
        """
        Generate response based on document content
        
        Args:
            query: User query
            relevant_docs: List of relevant document chunks
            
        Returns:
            Dictionary with response and sources
        """
        if not relevant_docs:
            return {
                'response': "I couldn't find relevant information in your documents for this query.",
                'sources': []
            }
        
        # Prepare context from documents
        context = self._format_document_context(relevant_docs)
        
        prompt = f"""You are a helpful assistant that answers questions based on provided document content.

Context from documents:
{context}

Question: {query}

Instructions:
- Answer the question using ONLY the information provided in the document context
- If the information is not available in the documents, say so clearly
- Cite specific documents and page numbers when possible
- Be comprehensive but concise
- If multiple documents contain relevant information, synthesize them appropriately

Answer:"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Format sources
            sources = []
            for doc in relevant_docs:
                metadata = doc['metadata']
                sources.append({
                    'type': 'document',
                    'filename': metadata.get('filename', 'Unknown'),
                    'page': metadata.get('page_start', 'N/A'),
                    'section': metadata.get('section', 'Content'),
                    'content': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                })
            
            return {
                'response': response.text or "I apologize, but I couldn't generate a response.",
                'sources': sources
            }
            
        except Exception as e:
            raise Exception(f"Error generating document response: {str(e)}")
    
    def generate_web_response(self, query: str, web_results: List[Dict]) -> Dict:
        """
        Generate response based on web search results
        
        Args:
            query: User query
            web_results: List of web search results
            
        Returns:
            Dictionary with response and sources
        """
        if not web_results:
            return {
                'response': "I couldn't find relevant information on the web for this query.",
                'sources': []
            }
        
        # Prepare context from web results
        context = self._format_web_context(web_results)
        
        prompt = f"""You are a helpful assistant that answers questions based on web search results.

Web search results:
{context}

Question: {query}

Instructions:
- Answer the question using the information from the web search results
- Synthesize information from multiple sources when relevant
- Be factual and cite sources appropriately
- If the search results don't contain sufficient information, mention this
- Provide a comprehensive but concise answer

Answer:"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Format sources
            sources = []
            for result in web_results:
                sources.append({
                    'type': 'web',
                    'title': result.get('title', 'Unknown'),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', ''),
                    'source_type': result.get('source', 'web')
                })
            
            return {
                'response': response.text or "I apologize, but I couldn't generate a response.",
                'sources': sources
            }
            
        except Exception as e:
            raise Exception(f"Error generating web response: {str(e)}")
    
    def generate_hybrid_response(self, query: str, relevant_docs: List[Dict], web_results: List[Dict]) -> Dict:
        """
        Generate response combining document and web sources
        
        Args:
            query: User query
            relevant_docs: List of relevant document chunks
            web_results: List of web search results
            
        Returns:
            Dictionary with response and sources
        """
        # Prepare contexts
        doc_context = self._format_document_context(relevant_docs) if relevant_docs else "No relevant document content found."
        web_context = self._format_web_context(web_results) if web_results else "No relevant web information found."
        
        prompt = f"""You are a helpful assistant that answers questions using both document content and web information.

Document Context:
{doc_context}

Web Information:
{web_context}

Question: {query}

Instructions:
- Combine information from both documents and web sources to provide a comprehensive answer
- Clearly distinguish between information from documents vs. web sources
- If there are conflicts between sources, mention this
- Prioritize document content for specific details about uploaded materials
- Use web information for context, current data, or additional explanations
- Be comprehensive but well-organized

Answer:"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Combine sources
            sources = []
            
            # Add document sources
            for doc in relevant_docs:
                metadata = doc['metadata']
                sources.append({
                    'type': 'document',
                    'filename': metadata.get('filename', 'Unknown'),
                    'page': metadata.get('page_start', 'N/A'),
                    'section': metadata.get('section', 'Content'),
                    'content': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                })
            
            # Add web sources
            for result in web_results:
                sources.append({
                    'type': 'web',
                    'title': result.get('title', 'Unknown'),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', ''),
                    'source_type': result.get('source', 'web')
                })
            
            return {
                'response': response.text or "I apologize, but I couldn't generate a response.",
                'sources': sources
            }
            
        except Exception as e:
            raise Exception(f"Error generating hybrid response: {str(e)}")
    
    def _format_document_context(self, docs: List[Dict]) -> str:
        """Format document chunks for context"""
        if not docs:
            return "No document content available."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            metadata = doc['metadata']
            filename = metadata.get('filename', 'Unknown')
            page = metadata.get('page_start', 'N/A')
            section = metadata.get('section', 'Content')
            content = doc['content']
            
            context_parts.append(f"""
Document {i}: {filename} (Page {page}, Section: {section})
Content: {content}
""")
        
        return "\n".join(context_parts)
    
    def _format_web_context(self, results: List[Dict]) -> str:
        """Format web search results for context"""
        if not results:
            return "No web information available."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Unknown')
            url = result.get('url', '')
            snippet = result.get('snippet', '')
            source_type = result.get('source', 'web')
            
            context_parts.append(f"""
Source {i}: {title} ({source_type})
URL: {url}
Content: {snippet}
""")
        
        return "\n".join(context_parts)
