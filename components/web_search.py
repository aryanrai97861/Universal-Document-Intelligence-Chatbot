import requests
import os
from typing import List, Dict, Optional

class WebSearch:
    """Handles web search using Serper.dev API"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        
        if not self.api_key:
            raise ValueError("SERPER_API_KEY environment variable is required")
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web using Serper.dev API
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results,
                'gl': 'us',  # Country
                'hl': 'en'   # Language
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Parse organic results
            if 'organic' in data:
                for result in data['organic'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'source': 'web'
                    })
            
            # Parse answer box if available
            if 'answerBox' in data:
                answer_box = data['answerBox']
                results.insert(0, {
                    'title': answer_box.get('title', 'Answer Box'),
                    'url': answer_box.get('link', ''),
                    'snippet': answer_box.get('answer', answer_box.get('snippet', '')),
                    'source': 'answer_box'
                })
            
            # Parse knowledge graph if available
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                results.insert(0, {
                    'title': kg.get('title', 'Knowledge Graph'),
                    'url': kg.get('website', ''),
                    'snippet': kg.get('description', ''),
                    'source': 'knowledge_graph'
                })
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"Web search API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Web search error: {str(e)}")
    
    def search_news(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Search for news articles
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of news results
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results,
                'type': 'news',
                'gl': 'us',
                'hl': 'en'
            }
            
            response = requests.post("https://google.serper.dev/news", headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'news' in data:
                for result in data['news'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'date': result.get('date', ''),
                        'source': 'news'
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"News search error: {str(e)}")
    
    def search_images(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Search for images
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of image results
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results,
                'type': 'images',
                'gl': 'us'
            }
            
            response = requests.post("https://google.serper.dev/images", headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'images' in data:
                for result in data['images'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),
                        'image_url': result.get('imageUrl', ''),
                        'source': 'image'
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"Image search error: {str(e)}")
