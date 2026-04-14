import requests
from utils.embeddings import generate_embedding
from utils.vector_store import vector_db
from config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL

def index_document(chunks: list[str], source_filename: str):
    """
    RAG Pipeline step 1:
    Iterate over document chunks, embed them, and store in ChromaDB.
    """
    if not chunks:
        return
    
    embeddings = []
    metadatas = []
    valid_chunks = []
    
    for i, chunk in enumerate(chunks):
        emb = generate_embedding(chunk)
        if emb:
            embeddings.append(emb)
            # Store metadata such as source filename and chunk index
            metadatas.append({"source": source_filename, "chunk_index": i})
            valid_chunks.append(chunk)
            
    if valid_chunks:
        vector_db.add_chunks(valid_chunks, embeddings, metadatas)


def answer_question(query: str) -> tuple[str, list[str]]:
    """
    RAG Pipeline step 2:
    Retrieve relevant chunks and generate an answer using Ollama strictly from context.
    """
    query_emb = generate_embedding(query)
    if not query_emb:
        return "Failed to generate embedding for the question.", []
    
    # Retrieve top 5 most relevant chunks from ChromaDB
    results = vector_db.query(query_embedding=query_emb, n_results=5)
    
    if not results['documents'] or not results['documents'][0]:
        return "I do not know based on the provided document.", []
        
    retrieved_chunks = results['documents'][0]
    
    # Build a strict RAG prompt ensuring it only uses the context
    context_str = "\n\n".join([f"--- Chunk {i+1} ---\n{chunk}" for i, chunk in enumerate(retrieved_chunks)])
    
    prompt = f"""You are a helpful assistant answering a user's question based strictly on the provided document excerpt.
If the answer cannot be found in the provided context, you must output exactly: "I do not know based on the provided document." 
Do not include any external knowledge or make up information.

Context:
{context_str}

Question: {query}
Answer:"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_CHAT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 4096
                }
            },
            timeout=300
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        
        # Fallback if the model returns nothing
        if not answer:
            answer = "I do not know based on the provided document."
            
        return answer, retrieved_chunks
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "An error occurred while generating the answer.", []
