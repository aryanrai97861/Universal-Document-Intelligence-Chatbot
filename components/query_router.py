import re
from typing import Dict, List

class QueryRouter:
    """Routes queries between document search and web search based on query analysis"""
    
    def __init__(self):
        # Keywords that suggest web search is needed
        self.web_keywords = {
            'temporal': ['latest', 'recent', 'current', 'today', 'now', '2024', '2025', 'this year'],
            'explanatory': ['explain', 'how does', 'what is', 'why does', 'how to'],
            'comparative': ['vs', 'versus', 'compare', 'comparison', 'alternative', 'better than'],
            'current_data': ['price', 'cost', 'stock', 'market', 'trend', 'news', 'update'],
            'general_knowledge': ['define', 'definition', 'meaning', 'who is', 'what are']
        }
        
        # Keywords that suggest document search
        self.document_keywords = [
            'according to', 'in the document', 'from the file', 'mentioned in',
            'states that', 'document says', 'written in', 'specified in'
        ]
    
    def route_query(self, query: str, has_documents: bool = True) -> Dict:
        """
        Determine the best route for a query
        
        Args:
            query: The user query
            has_documents: Whether documents are available
            
        Returns:
            Dictionary with route decision and confidence
        """
        query_lower = query.lower()
        
        # If no documents available, always use web search
        if not has_documents:
            return {
                'route': 'web',
                'confidence': 1.0,
                'reason': 'No documents available'
            }
        
        # Calculate scores for different routes
        web_score = self._calculate_web_score(query_lower)
        document_score = self._calculate_document_score(query_lower)
        
        # Decision logic
        if web_score > 0.7:
            return {
                'route': 'web',
                'confidence': web_score,
                'reason': 'Query suggests need for current/external information'
            }
        elif document_score > 0.6:
            return {
                'route': 'document',
                'confidence': document_score,
                'reason': 'Query appears to reference document content'
            }
        elif web_score > 0.4 and document_score > 0.4:
            return {
                'route': 'hybrid',
                'confidence': (web_score + document_score) / 2,
                'reason': 'Query could benefit from both sources'
            }
        else:
            # Default to document search for uploaded documents
            return {
                'route': 'document',
                'confidence': 0.5,
                'reason': 'Default to document search'
            }
    
    def _calculate_web_score(self, query: str) -> float:
        """Calculate confidence score for web search routing"""
        score = 0.0
        total_checks = 0
        
        for category, keywords in self.web_keywords.items():
            category_score = 0
            for keyword in keywords:
                if keyword in query:
                    category_score += 1
            
            # Normalize by category size and add to total
            if keywords:
                score += min(category_score / len(keywords), 1.0) * 0.2
                total_checks += 1
        
        # Check for question patterns that often need web search
        question_patterns = [
            r'\bhow\s+(?:to|do|does|can)\b',
            r'\bwhat\s+(?:is|are|does)\b',
            r'\bwhy\s+(?:is|are|does|do)\b',
            r'\bwhen\s+(?:is|are|was|were)\b',
            r'\bwhere\s+(?:is|are|can)\b'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, query):
                score += 0.3
                break
        
        # Check for current time references
        time_patterns = [
            r'\b(today|now|currently|this\s+(?:year|month|week))\b',
            r'\b202[4-9]\b',  # Recent years
            r'\b(?:latest|recent|new|updated)\b'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, query):
                score += 0.4
                break
        
        return min(score, 1.0)
    
    def _calculate_document_score(self, query: str) -> float:
        """Calculate confidence score for document search routing"""
        score = 0.0
        
        # Check for explicit document references
        for keyword in self.document_keywords:
            if keyword in query:
                score += 0.5
        
        # Check for specific document query patterns
        document_patterns = [
            r'\bin\s+(?:the|this|that)\s+(?:document|file|pdf|report)\b',
            r'\baccording\s+to\b',
            r'\bmentioned\s+(?:in|above|below)\b',
            r'\bsection\s+\d+\b',
            r'\bpage\s+\d+\b',
            r'\bchapter\s+\d+\b'
        ]
        
        for pattern in document_patterns:
            if re.search(pattern, query):
                score += 0.3
        
        # Check for specific content queries (less likely to need web search)
        specific_patterns = [
            r'\bwhat\s+does\s+(?:the|this)\s+document\s+say\b',
            r'\bfind\s+(?:in|from)\s+(?:the|this)\b',
            r'\bsummarize\s+(?:the|this)\b',
            r'\blist\s+(?:all|the)\b'
        ]
        
        for pattern in specific_patterns:
            if re.search(pattern, query):
                score += 0.4
        
        return min(score, 1.0)
    
    def explain_routing(self, query: str, has_documents: bool = True) -> str:
        """
        Provide explanation for routing decision
        
        Args:
            query: The user query
            has_documents: Whether documents are available
            
        Returns:
            Human-readable explanation
        """
        decision = self.route_query(query, has_documents)
        
        explanations = {
            'web': "I'll search the web because this query involves current information, comparisons, or general knowledge that may not be in your documents.",
            'document': "I'll search your uploaded documents because this query appears to be asking about specific content you've provided.",
            'hybrid': "I'll search both your documents and the web to provide a comprehensive answer combining your specific content with current information."
        }
        
        return explanations.get(decision['route'], "I'll search your documents by default.")
