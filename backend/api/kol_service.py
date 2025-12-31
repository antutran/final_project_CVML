"""
KOL (Key Opinion Leader) management service.

Handles listing, loading, and managing KOL style clusters.
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src2.config import KOL_STYLE_ROOT


class KOLService:
    """Service for managing KOL styles and clusters."""
    
    def __init__(self, kol_dir: Path = None):
        """
        Initialize KOL service.
        
        Args:
            kol_dir: Directory containing KOL cluster files (default: from config)
        """
        self.kol_dir = Path(kol_dir) if kol_dir else KOL_STYLE_ROOT
        
        if not self.kol_dir.exists():
            raise FileNotFoundError(f"KOL directory not found: {self.kol_dir}")
    
    def list_kols(self) -> List[Dict[str, Any]]:
        """
        List all available KOL styles.
        
        Returns:
            List of KOL info dicts with keys: id, style, name, file_path
        """
        kols = []
        
        for kol_file in sorted(self.kol_dir.glob("KOL_*.npy")):
            # Parse filename: KOL_{style}_{name}_clusters.npy
            filename = kol_file.stem  # Remove .npy extension
            
            # Remove "KOL_" prefix and "_clusters" suffix
            if filename.startswith("KOL_") and filename.endswith("_clusters"):
                content = filename[4:-9]  # Remove "KOL_" and "_clusters"
                
                # Split into parts
                parts = content.split("_")
                
                if len(parts) >= 2:
                    style = parts[0]
                    name = "_".join(parts[1:])  # Handle multi-word names
                    
                    kol_id = f"{style}_{name}"
                    
                    kols.append({
                        "id": kol_id,
                        "style": style,
                        "name": name.replace("_", " "),
                        "file_path": str(kol_file),
                        "display_name": f"{style.capitalize()} - {name.replace('_', ' ')}"
                    })
        
        return kols
    
    def load_kol(self, kol_id: str) -> np.ndarray:
        """
        Load KOL cluster embeddings by ID.
        
        Args:
            kol_id: KOL identifier (e.g., "feminine_Josefine_Vogt")
            
        Returns:
            KOL cluster embeddings array
            
        Raises:
            FileNotFoundError: If KOL file not found
        """
        # Construct filename
        kol_file = self.kol_dir / f"KOL_{kol_id}_clusters.npy"
        
        if not kol_file.exists():
            raise FileNotFoundError(f"KOL cluster file not found: {kol_file}")
        
        return np.load(kol_file)
    
    def get_kol_info(self, kol_id: str) -> Dict[str, Any]:
        """
        Get information about a specific KOL.
        
        Args:
            kol_id: KOL identifier
            
        Returns:
            KOL info dict
            
        Raises:
            ValueError: If KOL not found
        """
        kols = self.list_kols()
        
        for kol in kols:
            if kol["id"] == kol_id:
                return kol
        
        raise ValueError(f"KOL not found: {kol_id}")
