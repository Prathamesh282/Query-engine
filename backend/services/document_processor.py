import os
import faiss
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.core.config import settings
import pypdf
import docx

class DocumentProcessor:
    """Handles document processing, embedding, and vector storage."""

    def __init__(self):
        # Load the pre-trained model for creating embeddings
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Initialize an in-memory FAISS index for vector storage
        # FAISS is highly efficient for similarity search
        self.index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
        
        # Simple list to store the actual text chunks corresponding to the vectors
        self.chunk_store: List[str] = []
        
        # Text splitter for intelligent chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def _extract_text_from_pdf(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return "".join(page.extract_text() for page in reader.pages)

    def _extract_text_from_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_text_from_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def process_documents(self, file_paths: List[str]):
        """
        Main method to process a batch of uploaded documents.
        This fulfills the batch processing requirement.
        """
        all_chunks = []
        for file_path in file_paths:
            content = ""
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                content = self._extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                content = self._extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                content = self._extract_text_from_txt(file_path)
            
            if content:
                # Chunk the extracted content
                chunks = self.text_splitter.split_text(content)
                all_chunks.extend(chunks)
        
        if all_chunks:
            # Generate embeddings for all chunks in a single batch for efficiency
            print(f"Generating embeddings for {len(all_chunks)} chunks...")
            embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)
            
            # Add embeddings to the FAISS index and store the text chunks
            self.index.add(np.array(embeddings, dtype=np.float32))
            self.chunk_store.extend(all_chunks)
            print(f"Successfully added {len(all_chunks)} chunks to the vector store.")
            print(f"Total chunks in store: {self.index.ntotal}")

    def search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Searches for relevant document chunks based on a query."""
        if self.index.ntotal == 0:
            return []
            
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding, dtype=np.float32), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1: # FAISS returns -1 for no result
                results.append({
                    "content": self.chunk_store[idx],
                    "score": distances[0][i]
                })
        return results