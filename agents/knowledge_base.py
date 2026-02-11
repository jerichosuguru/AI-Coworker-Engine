"""
Knowledge Base with RAG (Retrieval-Augmented Generation)
"""
import faiss
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import KNOWLEDGE_BASE_DIR, EMBEDDING_MODEL, TOP_K_RETRIEVAL


class KnowledgeBase:
    """
    RAG system for NPC knowledge retrieval

    Features:
    - Vector similarity search
    - Document chunking
    - Relevance scoring
    - Cache for frequently accessed docs
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = str(KNOWLEDGE_BASE_DIR)

        self.data_dir = Path(data_dir)

        # Load embedding model
        print(f"🔄 Loading embedding model: {EMBEDDING_MODEL}...")
        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"⚠️  Could not load embedding model: {e}")
            self.embedding_model = None

        # Storage
        self.documents: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index: Optional[faiss.Index] = None

        # Cache
        self.query_cache: Dict[str, List[Dict]] = {}

    def load_documents(self):
        """Load and index all knowledge base documents"""
        # Create data directory if not exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load Gucci context
        gucci_doc = self._load_file("gucci_context.txt")
        if gucci_doc:
            self._add_document(
                content=gucci_doc,
                metadata={"source": "gucci_context", "type": "company_info"}
            )

        # Load competency framework
        framework_doc = self._load_file("competency_framework.txt")
        if framework_doc:
            self._add_document(
                content=framework_doc,
                metadata={"source": "competency_framework", "type": "hr_framework"}
            )

        # Load HR best practices
        hr_practices = self._load_file("hr_best_practices.txt")
        if hr_practices:
            self._add_document(
                content=hr_practices,
                metadata={"source": "hr_best_practices", "type": "guidelines"}
            )

        # Build FAISS index
        if self.documents and self.embedding_model:
            self._build_index()
            print(f"✅ Loaded {len(self.documents)} documents into knowledge base")
        elif not self.documents:
            print("⚠️  No documents found in knowledge base directory")
            print(f"   Create files in: {self.data_dir}")
        else:
            print("⚠️  Embedding model not available, skipping indexing")

    def _load_file(self, filename: str) -> Optional[str]:
        """Load text file"""
        filepath = self.data_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️  Error reading {filepath}: {e}")
                return None
        else:
            print(f"ℹ️  File not found: {filepath}")
        return None

    def _add_document(self, content: str, metadata: Dict):
        """Add document with chunking"""
        # Chunk document (simple sentence-based chunking)
        chunks = self._chunk_text(content, chunk_size=500, overlap=50)

        for i, chunk in enumerate(chunks):
            self.documents.append({
                "id": f"{metadata['source']}_chunk_{i}",
                "content": chunk,
                "metadata": metadata,
                "chunk_index": i
            })

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks

    def _build_index(self):
        """Build FAISS index for fast similarity search"""
        if not self.documents or not self.embedding_model:
            return

        # Extract document contents
        contents = [doc["content"] for doc in self.documents]

        # Generate embeddings
        print("🔄 Generating embeddings for knowledge base...")
        try:
            self.embeddings = self.embedding_model.encode(
                contents,
                show_progress_bar=True,
                convert_to_numpy=True
            )

            # Create FAISS index
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)  # L2 distance
            self.index.add(self.embeddings.astype('float32'))

            print(f"✅ Built FAISS index with {len(self.documents)} vectors")
        except Exception as e:
            print(f"❌ Error building index: {e}")

    def search(
        self,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search knowledge base for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of relevant document chunks with scores
        """
        # Check cache
        cache_key = f"{query}_{top_k}_{filter_metadata}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        if not self.index or not self.documents or not self.embedding_model:
            return []

        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)

            # Search FAISS index
            distances, indices = self.index.search(
                query_embedding.astype('float32'),
                min(top_k * 2, len(self.documents))  # Get more, then filter
            )

            # Retrieve documents
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[int(idx)]

                    # Apply metadata filter if provided
                    if filter_metadata:
                        if not all(doc["metadata"].get(k) == v for k, v in filter_metadata.items()):
                            continue

                    results.append({
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "score": float(dist),
                        "chunk_id": doc["id"]
                    })

                    if len(results) >= top_k:
                        break

            # Cache results
            self.query_cache[cache_key] = results

            return results
        except Exception as e:
            print(f"⚠️  Search error: {e}")
            return []

    def get_context_for_npc(
        self,
        npc_id: str,
        user_query: str,
        top_k: int = TOP_K_RETRIEVAL
    ) -> str:
        """Get relevant context for specific NPC"""
        # NPC-specific filters
        npc_filters = {
            "chro": {"type": "hr_framework"},
            "ceo": {"type": "company_info"},
            "regional_manager": {"type": "guidelines"}
        }

        filter_metadata = npc_filters.get(npc_id)

        # Search
        results = self.search(user_query, top_k=top_k, filter_metadata=filter_metadata)

        # Format context
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Context {i}]: {result['content']}")

        return "\n\n".join(context_parts)


# Initialize global knowledge base
knowledge_base = KnowledgeBase()