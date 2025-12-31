"""
Embedding generation service for user-uploaded images.

Adapts the logic from src1/build_user_style.py and src1/embed_all_folders.py
to work with uploaded images in a session.
"""

import numpy as np
import joblib
from PIL import Image
from pathlib import Path
from typing import List, Optional
import sys

# Try to import CLIP (optional dependency)
try:
    import clip
    import torch
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    clip = None
    torch = None

# Add parent directory to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src2.config import BASE_DIR


class EmbeddingService:
    """Service for generating user style embeddings from uploaded images."""
    
    def __init__(self, pca_path: Path = None, device: str = None):
        """
        Initialize embedding service.
        
        Args:
            pca_path: Path to PCA model (default: models/pca_30d.joblib)
            device: Device for CLIP model (default: auto-detect)
            
        Raises:
            RuntimeError: If CLIP is not available
        """
        if not CLIP_AVAILABLE:
            raise RuntimeError(
                "CLIP is not installed. Install it with: "
                "pip install git+https://github.com/openai/CLIP.git torch"
            )
        
        self.pca_path = pca_path or (BASE_DIR / "models" / "pca_30d.joblib")
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load CLIP model
        print(f"Loading CLIP model on {self.device}...")
        self.clip_model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.clip_model.eval()
        
        # Load PCA model
        print(f"Loading PCA model from {self.pca_path}...")
        if not self.pca_path.exists():
            raise FileNotFoundError(f"PCA model not found: {self.pca_path}")
        
        self.pca = joblib.load(self.pca_path)
    
    def embed_images(self, image_paths: List[Path]) -> np.ndarray:
        """
        Generate 512D CLIP embeddings from images.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Array of shape (N, 512) with normalized embeddings
        """
        if not image_paths:
            raise ValueError("No images provided")
        
        embeddings = []
        
        with torch.no_grad():
            for img_path in image_paths:
                # Load and preprocess image
                img = Image.open(img_path).convert("RGB")
                img_tensor = self.preprocess(img).unsqueeze(0).to(self.device)
                
                # Generate embedding
                emb = self.clip_model.encode_image(img_tensor)
                
                # Normalize
                emb = emb / emb.norm(dim=-1, keepdim=True)
                
                embeddings.append(emb.cpu().numpy())
        
        return np.vstack(embeddings)  # Shape: (N, 512)
    
    def generate_user_style(self, image_paths: List[Path]) -> np.ndarray:
        """
        Generate 30D user style vector from uploaded images.
        
        This follows the pipeline from build_user_style.py:
        1. Generate 512D CLIP embeddings
        2. Compute centroid in 512D space
        3. Apply PCA to reduce to 30D
        4. Normalize
        
        Args:
            image_paths: List of paths to user images
            
        Returns:
            30D user style vector (normalized)
        """
        # Generate 512D embeddings
        embeddings_512d = self.embed_images(image_paths)
        
        # Normalize each embedding
        embeddings_512d = embeddings_512d / np.linalg.norm(
            embeddings_512d, axis=1, keepdims=True
        )
        
        # Compute centroid in 512D space
        centroid_512 = embeddings_512d.mean(axis=0)
        centroid_512 = centroid_512 / np.linalg.norm(centroid_512)
        
        # Apply PCA to reduce to 30D
        centroid_30 = self.pca.transform(centroid_512.reshape(1, -1))[0]
        
        # Normalize
        centroid_30 = centroid_30 / np.linalg.norm(centroid_30)
        
        return centroid_30.astype(np.float32)
