"""
Session management for AI fashion recommendation API.

Handles session creation, state persistence, and file management
for user uploads and embeddings.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import numpy as np

from src3.anti_repeat import AntiRepeatMemory
from src3.alpha_state import default_state


class SessionManager:
    """
    Manages user sessions with in-memory storage and disk persistence.
    
    Each session contains:
    - session_id: Unique identifier
    - gender: "male" or "female"
    - user_vec: 30D user style vector (after PCA)
    - kol_clusters: Selected KOL cluster embeddings
    - kol_name: Selected KOL identifier
    - state: Alpha/beta/pref and alpha_stats
    - anti_repeat: AntiRepeatMemory instance
    - created_at: Timestamp
    - last_activity: Timestamp
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialize session manager.
        
        Args:
            base_dir: Root directory for session data storage
        """
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.uploads_dir = self.base_dir / "uploads"
        
        # Create directories
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory session storage
        self._sessions: Dict[str, Dict[str, Any]] = {}
        
        # Load existing sessions from disk
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load all existing sessions from disk into memory."""
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                session_id = session_file.stem
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Reconstruct session in memory
                self._sessions[session_id] = {
                    "session_id": session_id,
                    "gender": session_data.get("gender"),
                    "kol_name": session_data.get("kol_name"),
                    "state": session_data.get("state", default_state()),
                    "created_at": session_data.get("created_at"),
                    "last_activity": session_data.get("last_activity"),
                    "user_vec": None,
                    "kol_clusters": None,
                    "anti_repeat": AntiRepeatMemory(maxlen=30, tau=8.0),
                }
                
                # Load numpy arrays if they exist
                user_vec_path = self.sessions_dir / session_id / "user_vec.npy"
                if user_vec_path.exists():
                    self._sessions[session_id]["user_vec"] = np.load(user_vec_path)
                
                kol_path = self.sessions_dir / session_id / "kol_clusters.npy"
                if kol_path.exists():
                    self._sessions[session_id]["kol_clusters"] = np.load(kol_path)
                
                # Restore anti-repeat memory
                anti_repeat_path = self.sessions_dir / session_id / "anti_repeat.json"
                if anti_repeat_path.exists():
                    with open(anti_repeat_path, 'r') as f:
                        anti_repeat_data = json.load(f)
                    # Restore item memory
                    for items in anti_repeat_data.get("item_memory", []):
                        self._sessions[session_id]["anti_repeat"].update([{"items": items}])
                
            except Exception as e:
                print(f"Warning: Could not load session {session_file.name}: {e}")
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self._sessions[session_id] = {
            "session_id": session_id,
            "gender": None,
            "user_vec": None,
            "kol_clusters": None,
            "kol_name": None,
            "state": default_state(),
            "anti_repeat": AntiRepeatMemory(maxlen=30, tau=8.0),
            "created_at": timestamp,
            "last_activity": timestamp,
        }
        
        # Create session directory
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to disk
        self._save_session(session_id)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dict or None if not found
        """
        session = self._sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
        return session
    
    def update_session(self, session_id: str, **kwargs):
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            **kwargs: Fields to update (gender, user_vec, kol_clusters, etc.)
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        
        # Update fields
        for key, value in kwargs.items():
            if key in session:
                session[key] = value
        
        session["last_activity"] = datetime.now().isoformat()
        
        # Save to disk
        self._save_session(session_id)
    
    def _save_session(self, session_id: str):
        """
        Save session to disk.
        
        Args:
            session_id: Session identifier
        """
        if session_id not in self._sessions:
            return
        
        session = self._sessions[session_id]
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON metadata
        json_data = {
            "session_id": session_id,
            "gender": session.get("gender"),
            "kol_name": session.get("kol_name"),
            "state": session.get("state"),
            "created_at": session.get("created_at"),
            "last_activity": session.get("last_activity"),
        }
        
        with open(self.sessions_dir / f"{session_id}.json", 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save numpy arrays
        if session.get("user_vec") is not None:
            np.save(session_dir / "user_vec.npy", session["user_vec"])
        
        if session.get("kol_clusters") is not None:
            np.save(session_dir / "kol_clusters.npy", session["kol_clusters"])
        
        # Save anti-repeat memory
        anti_repeat = session.get("anti_repeat")
        if anti_repeat:
            anti_repeat_data = {
                "item_memory": [list(items) for items in anti_repeat.item_memory]
            }
            with open(session_dir / "anti_repeat.json", 'w') as f:
                json.dump(anti_repeat_data, f, indent=2)
    
    def get_upload_dir(self, session_id: str) -> Path:
        """
        Get upload directory for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to upload directory
        """
        upload_dir = self.uploads_dir / session_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    def reset_session_state(self, session_id: str):
        """
        Reset alpha/beta/pref state for a session while keeping user data.
        
        Args:
            session_id: Session identifier
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        session["state"] = default_state()
        session["anti_repeat"] = AntiRepeatMemory(maxlen=30, tau=8.0)
        session["last_activity"] = datetime.now().isoformat()
        
        self._save_session(session_id)
    
    def delete_session(self, session_id: str):
        """
        Delete a session and all associated files.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        # Delete session files
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        
        session_dir = self.sessions_dir / session_id
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)
        
        # Delete uploads
        upload_dir = self.uploads_dir / session_id
        if upload_dir.exists():
            import shutil
            shutil.rmtree(upload_dir)
