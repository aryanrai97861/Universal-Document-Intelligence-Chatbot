from components.document_processor import DocumentProcessor
from components.vector_store import VectorStore

def run_smoke_test():
    print("Starting smoke test: create sample chunk, index, and query...")

    # Create a sample document chunk
    sample_text = (
        "This is a sample document about machine learning and natural language processing. "
        "It explains basics like supervised learning, transformers, and evaluation metrics. "
        "The document also mentions vector embeddings and semantic search."
    )

    chunks = [{
        'content': sample_text,
        'metadata': {
            'filename': 'sample_document.pdf',
            'section': 'Introduction',
            'page_start': 1,
            'page_end': 1,
            'chunk_index': 0,
            'chunk_size': len(sample_text)
        }
    }]

    # Initialize VectorStore
    vs = VectorStore()

    # Clear any existing data to keep test deterministic
    try:
        vs.clear()
    except Exception:
        pass

    # Add documents
    vs.add_documents(chunks)
    print("Added sample chunk to vector store.")

    # Run a semantic search
    query = "What is semantic search and embeddings?"
    results = vs.search(query, k=3)

    print(f"Search results for: '{query}'")
    for i, r in enumerate(results, 1):
        print(f"Result {i} - id: {r.get('id')}, distance: {r.get('distance')}")
        print(f"Metadata: {r.get('metadata')}")
        print(f"Content (truncated): {r.get('content')[:200]}\n---")

    stats = vs.get_stats()
    print(f"Vector store stats: {stats}")

if __name__ == '__main__':
    run_smoke_test()
