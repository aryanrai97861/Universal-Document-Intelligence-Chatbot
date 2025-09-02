import PyPDF2
import re
from typing import List, Dict
from pathlib import Path

class DocumentProcessor:
    """Handles PDF document processing and intelligent text chunking"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_pdf(self, file_path: str, filename: str) -> List[Dict]:
        """
        Process a PDF file and return chunks with metadata
        
        Args:
            file_path: Path to the PDF file
            filename: Original filename
            
        Returns:
            List of chunks with metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                page_texts = []
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    page_texts.append({
                        'page_num': page_num + 1,
                        'text': page_text
                    })
                    full_text += f"\n[Page {page_num + 1}]\n{page_text}"
                
                # Create intelligent chunks
                chunks = self._create_intelligent_chunks(full_text, filename, page_texts)
                
                return chunks
                
        except Exception as e:
            raise Exception(f"Error processing PDF {filename}: {str(e)}")
    
    def _create_intelligent_chunks(self, text: str, filename: str, page_texts: List[Dict]) -> List[Dict]:
        """
        Create intelligent chunks preserving document structure
        
        Args:
            text: Full document text
            filename: Source filename
            page_texts: List of page texts with page numbers
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # Split by paragraphs and sections first
        sections = self._split_by_sections(text)
        
        for section in sections:
            # Further split large sections into smaller chunks
            section_chunks = self._split_text_recursive(section['text'])
            
            for i, chunk_text in enumerate(section_chunks):
                # Find which page(s) this chunk belongs to
                page_info = self._find_page_numbers(chunk_text, page_texts)
                
                chunk = {
                    'content': chunk_text.strip(),
                    'metadata': {
                        'filename': filename,
                        'section': section.get('title', 'Content'),
                        'page_start': page_info['start_page'],
                        'page_end': page_info['end_page'],
                        'chunk_index': len(chunks),
                        'chunk_size': len(chunk_text)
                    }
                }
                chunks.append(chunk)
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[Dict]:
        """
        Split text by sections, trying to identify headers and structure
        
        Args:
            text: Input text
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        
        # Common header patterns
        header_patterns = [
            r'^[A-Z\s]{3,}$',  # ALL CAPS headers
            r'^\d+\.\s+[A-Z].*$',  # Numbered headers
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:?\s*$',  # Title Case headers
            r'^\*\*.*\*\*$',  # Bold markdown headers
            r'^#+\s+.*$',  # Markdown headers
        ]
        
        lines = text.split('\n')
        current_section = {'title': 'Introduction', 'text': ''}
        
        for line in lines:
            line = line.strip()
            if not line:
                current_section['text'] += '\n'
                continue
            
            # Check if line is a header
            is_header = False
            for pattern in header_patterns:
                if re.match(pattern, line):
                    is_header = True
                    break
            
            if is_header and len(current_section['text'].strip()) > 50:
                # Save current section and start new one
                sections.append(current_section)
                current_section = {'title': line, 'text': ''}
            else:
                current_section['text'] += line + '\n'
        
        # Add the last section
        if current_section['text'].strip():
            sections.append(current_section)
        
        return sections
    
    def _split_text_recursive(self, text: str) -> List[str]:
        """
        Recursively split text into chunks with overlap
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a good breaking point (sentence end)
            break_point = self._find_sentence_break(text, start, end)
            
            if break_point == -1:
                # No good break point found, use hard limit
                break_point = end
            
            chunks.append(text[start:break_point])
            start = break_point - self.chunk_overlap
            
            # Ensure we don't go backwards
            if start < 0:
                start = 0
        
        return chunks
    
    def _find_sentence_break(self, text: str, start: int, end: int) -> int:
        """
        Find the best sentence break point within a range
        
        Args:
            text: Input text
            start: Start position
            end: End position
            
        Returns:
            Best break point or -1 if none found
        """
        # Look for sentence endings near the end
        search_start = max(start, end - 200)
        
        # Sentence ending patterns
        sentence_ends = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        
        best_break = -1
        for pattern in sentence_ends:
            pos = text.rfind(pattern, search_start, end)
            if pos != -1:
                best_break = max(best_break, pos + len(pattern))
        
        return best_break
    
    def _find_page_numbers(self, chunk_text: str, page_texts: List[Dict]) -> Dict:
        """
        Find which page(s) a chunk belongs to
        
        Args:
            chunk_text: The chunk text
            page_texts: List of page texts with page numbers
            
        Returns:
            Dictionary with start_page and end_page
        """
        start_page = None
        end_page = None
        
        # Sample first and last 100 characters of chunk
        chunk_start = chunk_text[:100].strip()
        chunk_end = chunk_text[-100:].strip()
        
        for page_info in page_texts:
            page_text = page_info['text']
            page_num = page_info['page_num']
            
            # Check if chunk start appears in this page
            if chunk_start in page_text and start_page is None:
                start_page = page_num
            
            # Check if chunk end appears in this page
            if chunk_end in page_text:
                end_page = page_num
        
        return {
            'start_page': start_page or 1,
            'end_page': end_page or start_page or 1
        }
