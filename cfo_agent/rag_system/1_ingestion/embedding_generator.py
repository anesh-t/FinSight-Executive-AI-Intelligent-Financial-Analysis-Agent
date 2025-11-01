"""
Embedding Generator - Generate vector embeddings for text chunks
Uses sentence-transformers to create 384-dimensional embeddings.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from pathlib import Path
import sys
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(
        self,
        model_name: str = None,
        batch_size: int = None,
        use_gpu: bool = None,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Model to use (default from config)
            batch_size: Batch size for encoding (default from config)
            use_gpu: Whether to use GPU (default from config)
            cache_dir: Cache directory for models (default from config)
        """
        self.model_name = model_name or config.embedding.model_name
        self.batch_size = batch_size or config.embedding.batch_size
        self.use_gpu = use_gpu if use_gpu is not None else config.embedding.use_gpu
        self.cache_dir = cache_dir or config.embedding.cache_dir
        
        print(f"🤖 Loading embedding model: {self.model_name}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   GPU: {self.use_gpu}")
        
        # Load model
        self.model = self._load_model()
        
        # Verify dimension
        test_emb = self.model.encode(["test"], show_progress_bar=False)
        self.dimension = test_emb.shape[1]
        print(f"   ✅ Model loaded! Dimension: {self.dimension}")
        print()
    
    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model"""
        try:
            # Set device
            device = 'cuda' if self.use_gpu else 'cpu'
            
            # Load model
            model = SentenceTransformer(
                self.model_name,
                device=device,
                cache_folder=self.cache_dir
            )
            
            return model
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def generate_embeddings(
        self,
        texts: List[str],
        show_progress: bool = True,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            show_progress: Show progress bar
            normalize: Normalize embeddings (for cosine similarity)
            
        Returns:
            numpy array of shape (len(texts), dimension)
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
            
            return embeddings
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            raise
    
    def generate_single_embedding(
        self,
        text: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string
            normalize: Normalize embedding
            
        Returns:
            1D numpy array of shape (dimension,)
        """
        embeddings = self.generate_embeddings(
            [text],
            show_progress=False,
            normalize=normalize
        )
        return embeddings[0]
    
    def verify_embeddings(self, embeddings: np.ndarray) -> dict:
        """
        Verify embedding quality.
        
        Returns:
            Dictionary with verification metrics
        """
        stats = {
            'shape': embeddings.shape,
            'dimension': embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings),
            'mean_norm': np.mean(np.linalg.norm(embeddings, axis=1)) if len(embeddings.shape) > 1 else np.linalg.norm(embeddings),
            'contains_nan': np.isnan(embeddings).any(),
            'contains_inf': np.isinf(embeddings).any()
        }
        
        return stats


def test_embedding_generator():
    """Test the embedding generator"""
    print("=" * 70)
    print("TESTING EMBEDDING GENERATOR")
    print("=" * 70)
    print()
    
    # Initialize
    generator = EmbeddingGenerator()
    
    # Test single embedding
    print("Test 1: Single embedding")
    text = "This is a test sentence about financial risks."
    embedding = generator.generate_single_embedding(text)
    print(f"  Text: {text}")
    print(f"  Embedding shape: {embedding.shape}")
    print(f"  Embedding norm: {np.linalg.norm(embedding):.4f}")
    print(f"  First 5 values: {embedding[:5]}")
    print()
    
    # Test batch embeddings
    print("Test 2: Batch embeddings")
    texts = [
        "Apple reported strong iPhone sales.",
        "Amazon's cloud revenue grew 20%.",
        "Google faces regulatory challenges.",
        "Microsoft Azure expanded globally.",
        "Meta invested in AI technology."
    ]
    embeddings = generator.generate_embeddings(texts, show_progress=False)
    print(f"  Number of texts: {len(texts)}")
    print(f"  Embeddings shape: {embeddings.shape}")
    print(f"  Expected: ({len(texts)}, {generator.dimension})")
    print()
    
    # Verify embeddings
    print("Test 3: Verification")
    stats = generator.verify_embeddings(embeddings)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Test similarity
    print("Test 4: Similarity test")
    similar_texts = [
        "The company faces regulatory risks.",
        "Regulatory challenges affect the business.",
        "The weather is nice today."
    ]
    similar_embs = generator.generate_embeddings(similar_texts, show_progress=False)
    
    # Cosine similarity (dot product since normalized)
    sim_1_2 = np.dot(similar_embs[0], similar_embs[1])
    sim_1_3 = np.dot(similar_embs[0], similar_embs[2])
    
    print(f"  Text 1: {similar_texts[0]}")
    print(f"  Text 2: {similar_texts[1]}")
    print(f"  Text 3: {similar_texts[2]}")
    print(f"  Similarity (1-2): {sim_1_2:.4f} (should be high)")
    print(f"  Similarity (1-3): {sim_1_3:.4f} (should be low)")
    print()
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    test_embedding_generator()
