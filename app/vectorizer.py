import math
import re
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

class TextVectorizer:
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.model = None
        self.use_st = False
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_st = True
        except Exception:
            self.use_st = False

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        words = re.findall(r'[a-zA-Z0-9\+#\.]+', text)
        tokens = list(words)
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")
        return tokens

    def fit(self, documents: List[str]):
        if self.use_st:
            return
        
        doc_count = len(documents)
        df: Dict[str, int] = {}
        
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for tok in tokens:
                df[tok] = df.get(tok, 0) + 1
                
        sorted_terms = sorted([t for t, count in df.items() if count >= 1], key=lambda x: df[x], reverse=True)
        self.vocab = {term: idx for idx, term in enumerate(sorted_terms[:self.embedding_dim])}
        
        self.idf = {
            term: math.log((doc_count + 1) / (df[term] + 1)) + 1.0
            for term in self.vocab
        }

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.use_st and self.model is not None:
            return self.model.encode(texts, normalize_embeddings=True)
        
        if not self.vocab and texts:
            self.fit(texts)
            
        vectors = np.zeros((len(texts), max(len(self.vocab), 1)), dtype=np.float32)
        
        for doc_idx, text in enumerate(texts):
            tokens = self._tokenize(text)
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
                
            for tok, count in tf.items():
                if tok in self.vocab:
                    col_idx = self.vocab[tok]
                    tf_val = 1 + math.log(count)
                    vectors[doc_idx, col_idx] = tf_val * self.idf.get(tok, 1.0)
                    
            norm = np.linalg.norm(vectors[doc_idx])
            if norm > 0:
                vectors[doc_idx] /= norm
                
        return vectors

class VectorIndex:
    def __init__(self, dim: int):
        self.dim = dim
        self.faiss_index = None
        self.vectors: Optional[np.ndarray] = None
        self.ids: List[str] = []
        
        try:
            import faiss
            self.faiss_index = faiss.IndexFlatIP(dim)
        except Exception:
            self.faiss_index = None

    def add(self, ids: List[str], vectors: np.ndarray):
        self.ids.extend(ids)
        if self.faiss_index is not None:
            import faiss
            vecs_copy = np.ascontiguousarray(vectors, dtype=np.float32)
            faiss.normalize_L2(vecs_copy)
            self.faiss_index.add(vecs_copy)
        else:
            if self.vectors is None:
                self.vectors = vectors.copy()
            else:
                self.vectors = np.vstack([self.vectors, vectors])

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> Tuple[List[str], List[float]]:
        if self.faiss_index is not None:
            q = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
            import faiss
            faiss.normalize_L2(q)
            distances, indices = self.faiss_index.search(q, min(top_k, len(self.ids)))
            ret_ids = [self.ids[i] for i in indices[0] if i < len(self.ids) and i >= 0]
            ret_scores = [float(s) for s in distances[0]]
            return ret_ids, ret_scores
        else:
            if self.vectors is None or len(self.ids) == 0:
                return [], []
            q = query_vector.reshape(1, -1)
            q_norm = np.linalg.norm(q)
            if q_norm > 0:
                q = q / q_norm
            similarities = np.dot(self.vectors, q.T).flatten()
            top_indices = np.argsort(-similarities)[:top_k]
            ret_ids = [self.ids[i] for i in top_indices]
            ret_scores = [float(similarities[i]) for i in top_indices]
            return ret_ids, ret_scores
