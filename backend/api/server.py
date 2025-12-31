"""
FastAPI server for AI fashion recommendation backend.

Provides RESTful API endpoints that wrap the existing recommendation pipeline.
"""

import sys
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from api.session_manager import SessionManager
from api.kol_service import KOLService
from api.embedding_service import EmbeddingService
from api.recommendation_service import RecommendationService
from api.item_service import ItemService
from src2.config import BASE_DIR, ITEM_EMB_ROOT


# Global services (initialized on startup)
session_manager: Optional[SessionManager] = None
kol_service: Optional[KOLService] = None
embedding_service: Optional[EmbeddingService] = None
item_service: Optional[ItemService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global session_manager, kol_service, embedding_service, item_service
    
    # SSL Fix for CLIP download
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    print("🚀 Starting AI Fashion Recommendation API...")
    print(f"📁 Base directory: {BASE_DIR}")
    
    # Initialize services
    session_manager = SessionManager(base_dir=BASE_DIR)
    kol_service = KOLService()
    item_service = ItemService(item_emb_root=ITEM_EMB_ROOT)
    
    # Initialize embedding service (may take time to load models)
    try:
        embedding_service = EmbeddingService()
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize embedding service: {e}")
        print("   Image upload and embedding endpoints will not work")
        embedding_service = None
    
    yield
    
    print("👋 Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="AI Fashion Recommendation API",
    description="Backend API for personalized fashion outfit recommendations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class SessionCreateResponse(BaseModel):
    session_id: str
    message: str


class GenderRequest(BaseModel):
    gender: str  # "male" or "female"


class KOLResponse(BaseModel):
    id: str
    style: str
    name: str
    display_name: str


class KOLSelectRequest(BaseModel):
    kol_id: str


class GenerateResponse(BaseModel):
    outfits: List[dict]
    alpha: float
    beta: float
    beta_used: float
    pref: float
    conf: float
    step: int


class FeedbackRequest(BaseModel):
    selected_indices: List[int]
    outfits: List[dict]


class FeedbackResponse(BaseModel):
    updated: bool
    reward: float
    pref: float
    conf: float
    beta: float


class StateResponse(BaseModel):
    session_id: str
    gender: Optional[str]
    kol_name: Optional[str]
    has_user_vec: bool
    has_kol_clusters: bool
    state: dict
    created_at: str
    last_activity: str


# ============================================================================
# Session Endpoints
# ============================================================================

@app.post("/api/session/create", response_model=SessionCreateResponse)
async def create_session():
    """Create a new user session."""
    session_id = session_manager.create_session()
    
    return {
        "session_id": session_id,
        "message": "Session created successfully"
    }


@app.get("/api/session/{session_id}/state", response_model=StateResponse)
async def get_session_state(session_id: str):
    """Get current session state."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "gender": session.get("gender"),
        "kol_name": session.get("kol_name"),
        "has_user_vec": session.get("user_vec") is not None,
        "has_kol_clusters": session.get("kol_clusters") is not None,
        "state": session.get("state", {}),
        "created_at": session.get("created_at", ""),
        "last_activity": session.get("last_activity", ""),
    }


@app.post("/api/session/{session_id}/reset")
async def reset_session(session_id: str):
    """Reset session state (alpha/beta/pref) while keeping user data."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_manager.reset_session_state(session_id)
    
    return {"message": "Session state reset successfully"}


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all associated data."""
    session_manager.delete_session(session_id)
    
    return {"message": "Session deleted successfully"}


# ============================================================================
# Gender Selection
# ============================================================================

@app.post("/api/session/{session_id}/gender")
async def set_gender(session_id: str, request: GenderRequest):
    """Set gender for the session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    gender = request.gender.lower()
    if gender not in ["male", "female"]:
        raise HTTPException(status_code=400, detail="Gender must be 'male' or 'female'")
    
    session_manager.update_session(session_id, gender=gender)
    
    return {"message": f"Gender set to {gender}"}


# ============================================================================
# KOL Selection
# ============================================================================

@app.get("/api/kol/list", response_model=List[KOLResponse])
async def list_kols():
    """List all available KOL styles."""
    kols = kol_service.list_kols()
    return kols


@app.post("/api/session/{session_id}/kol")
async def select_kol(session_id: str, request: KOLSelectRequest):
    """Select a KOL style for the session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Load KOL clusters
        kol_clusters = kol_service.load_kol(request.kol_id)
        
        # Update session
        session_manager.update_session(
            session_id,
            kol_clusters=kol_clusters,
            kol_name=request.kol_id
        )
        
        return {"message": f"KOL '{request.kol_id}' selected successfully"}
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Image Upload & Embedding
# ============================================================================

@app.post("/api/session/{session_id}/upload")
async def upload_images(session_id: str, files: List[UploadFile] = File(...)):
    """Upload user images to session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Get upload directory for this session
    upload_dir = session_manager.get_upload_dir(session_id)
    
    # Save uploaded files
    saved_files = []
    for i, file in enumerate(files):
        # Generate filename
        file_ext = Path(file.filename).suffix or ".jpg"
        file_path = upload_dir / f"image_{i}{file_ext}"
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        saved_files.append(str(file_path))
    
    return {
        "message": f"Uploaded {len(saved_files)} images successfully",
        "file_count": len(saved_files),
        "files": saved_files
    }


@app.post("/api/session/{session_id}/embed")
async def generate_embeddings(session_id: str):
    """Generate user style embeddings from uploaded images."""
    if embedding_service is None:
        raise HTTPException(
            status_code=503, 
            detail="Embedding service not available. CLIP model may not be installed."
        )
    
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get uploaded images
    upload_dir = session_manager.get_upload_dir(session_id)
    image_files = sorted(upload_dir.glob("image_*"))
    
    if not image_files:
        raise HTTPException(
            status_code=400, 
            detail="No images found. Please upload images first."
        )
    
    try:
        # Generate user style vector
        user_vec = embedding_service.generate_user_style(image_files)
        
        # Update session
        session_manager.update_session(session_id, user_vec=user_vec)
        
        return {
            "message": "User style vector generated successfully",
            "image_count": len(image_files),
            "vector_shape": user_vec.shape
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


# ============================================================================
# Outfit Generation
# ============================================================================

@app.post("/api/session/{session_id}/generate", response_model=GenerateResponse)
async def generate_outfits(
    session_id: str,
    auto_learn: bool = True,
    manual_alpha: Optional[float] = None,
    manual_beta: Optional[float] = None,
    diversity: bool = False,
):
    """
    Generate outfit recommendations.
    
    Args:
        session_id: Session ID
        auto_learn: If True, use UCB for alpha and auto-update beta. If False, use manual values.
        manual_alpha: Manual alpha value (0-1), used when auto_learn=False
        manual_beta: Manual beta value (0-1), used when auto_learn=False
        diversity: If True, increase diversity in outfit generation
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate session has required data
    if session.get("user_vec") is None:
        raise HTTPException(
            status_code=400, 
            detail="User style vector not set. Please upload images and generate embeddings first."
        )
    
    if session.get("kol_clusters") is None:
        raise HTTPException(
            status_code=400, 
            detail="KOL not selected. Please select a KOL style first."
        )
    
    if session.get("gender") is None:
        raise HTTPException(
            status_code=400, 
            detail="Gender not set. Please set gender first."
        )
    
    try:
        # Generate outfits
        result = RecommendationService.generate_outfits(
            user_vec=session["user_vec"],
            kol_clusters=session["kol_clusters"],
            gender=session["gender"],
            state=session["state"],
            anti_repeat=session["anti_repeat"],
            auto_learn=auto_learn,
            manual_alpha=manual_alpha,
            manual_beta=manual_beta,
            diversity=diversity,
        )
        
        # Save updated state
        session_manager.update_session(session_id, state=session["state"])
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Outfit generation failed: {str(e)}"
        )


# ============================================================================
# Feedback
# ============================================================================

@app.post("/api/session/{session_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(session_id: str, request: FeedbackRequest):
    """Submit feedback on recommended outfits."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate required data
    if session.get("user_vec") is None or session.get("kol_clusters") is None:
        raise HTTPException(
            status_code=400, 
            detail="Session not fully initialized"
        )
    
    try:
        # Process feedback
        feedback_result = RecommendationService.process_feedback(
            selected_indices=request.selected_indices,
            outfits=request.outfits,
            user_vec=session["user_vec"],
            kol_clusters=session["kol_clusters"],
            state=session["state"],
            anti_repeat=session["anti_repeat"],
        )
        
        # Save updated state
        session_manager.update_session(session_id, state=session["state"])
        
        return feedback_result
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Feedback processing failed: {str(e)}"
        )



# ============================================================================
# Image Serving
# ============================================================================

@app.get("/api/kol/{kol_id}/image")
async def get_kol_image(kol_id: str):
    """Serve a KOL image."""
    try:
        # 1. Try to serve from frontend/KOL directory
        # In Docker: ROOT = /app, so we want /app/frontend/KOL
        frontend_kol_dir = ROOT / "frontend" / "KOL"
        image_path = frontend_kol_dir / f"KOL_{kol_id}_clusters.jpg"
        
        if image_path.exists():
            from fastapi.responses import FileResponse
            return FileResponse(image_path)
            
        # 2. Fallback to error
        raise HTTPException(status_code=404, detail=f"KOL image not found: {kol_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving KOL image: {str(e)}")

@app.get("/api/item/{item_id}/image")
async def get_item_image(item_id: str):
    """Serve an item image by ID."""
    image_path = item_service.get_image_path(item_id)
    if not image_path:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found in cache")
    
    path = Path(image_path)
    if not path.exists():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"https://via.placeholder.com/400x600/EEEEEE/999999?text={item_id}")
    
    from fastapi.responses import FileResponse
    return FileResponse(path)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "AI Fashion Recommendation API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "session_manager": session_manager is not None,
            "kol_service": kol_service is not None,
            "embedding_service": embedding_service is not None,
        }
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
