# AI Fashion Recommendation API

Complete backend API for the AI fashion recommendation system, wrapping the existing research-grade recommendation pipeline.

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/tuantran/Downloads/CVML/backend

# Install basic API dependencies
python3 -m pip install fastapi uvicorn python-multipart pydantic requests

# Install ML dependencies (optional, needed for embedding service)
python3 -m pip install torch pillow numpy scikit-learn joblib
python3 -m pip install git+https://github.com/openai/CLIP.git
```

### 2. Start the API Server

```bash
cd /Users/tuantran/Downloads/CVML/backend
python3 -m uvicorn api.server:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Session Management

- **POST** `/api/session/create` - Create a new session
- **GET** `/api/session/{session_id}/state` - Get session state
- **POST** `/api/session/{session_id}/reset` - Reset session state
- **DELETE** `/api/session/{session_id}` - Delete session

### Gender & KOL Selection

- **POST** `/api/session/{session_id}/gender` - Set gender (male/female)
- **GET** `/api/kol/list` - List all available KOL styles
- **POST** `/api/session/{session_id}/kol` - Select a KOL style

### Image Upload & Embedding

- **POST** `/api/session/{session_id}/upload` - Upload user images
- **POST** `/api/session/{session_id}/embed` - Generate user style embeddings

### Outfit Recommendation

- **POST** `/api/session/{session_id}/generate` - Generate outfit recommendations
- **POST** `/api/session/{session_id}/feedback` - Submit feedback on outfits

### Health Check

- **GET** `/` - API root
- **GET** `/health` - Health check

## Complete Workflow Example

```bash
# 1. Create session
curl -X POST http://localhost:8000/api/session/create
# Returns: {"session_id": "abc-123-def", ...}

# 2. Set gender
curl -X POST http://localhost:8000/api/session/abc-123-def/gender \
  -H "Content-Type: application/json" \
  -d '{"gender": "female"}'

# 3. List available KOLs
curl http://localhost:8000/api/kol/list

# 4. Select a KOL
curl -X POST http://localhost:8000/api/session/abc-123-def/kol \
  -H "Content-Type: application/json" \
  -d '{"kol_id": "feminine_Josefine_Vogt"}'

# 5. Upload images (multipart form-data)
curl -X POST http://localhost:8000/api/session/abc-123-def/upload \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg"

# 6. Generate embeddings
curl -X POST http://localhost:8000/api/session/abc-123-def/embed

# 7. Generate outfits
curl -X POST http://localhost:8000/api/session/abc-123-def/generate

# 8. Submit feedback
curl -X POST http://localhost:8000/api/session/abc-123-def/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "selected_indices": [0, 2, 5],
    "outfits": [...]
  }'

# 9. Generate again (with updated preferences)
curl -X POST http://localhost:8000/api/session/abc-123-def/generate
```

## Architecture

```
backend/
├── api/
│   ├── server.py              # FastAPI application
│   ├── session_manager.py     # Session state management
│   ├── kol_service.py         # KOL loading and management
│   ├── embedding_service.py   # Image → style vector pipeline
│   └── recommendation_service.py  # Outfit generation & feedback
├── src2/
│   ├── config.py             # Configuration (updated for dynamic paths)
│   ├── model2.py             # Candidate item selection
│   └── kol_condition.py      # KOL conditioning
├── src3/
│   ├── model3.py             # Outfit generation & scoring
│   ├── alpha_online.py       # Alpha/beta/pref update logic
│   ├── alpha_state.py        # State persistence
│   └── anti_repeat.py        # Anti-repeat memory
└── sessions/                 # Session data (created at runtime)
    └── {session_id}/
        ├── user_vec.npy
        ├── kol_clusters.npy
        └── anti_repeat.json
```

## Key Features

✅ **Stateless API**: Each request is independent, state managed via sessions  
✅ **Preserves existing logic**: All recommendation algorithms unchanged  
✅ **Session persistence**: State saved to disk, survives server restarts  
✅ **Dynamic paths**: No hardcoded paths, works on any machine  
✅ **CORS enabled**: Works with frontend on different port  
✅ **Type-safe**: Pydantic models for request/response validation  

## Frontend Integration

Update frontend to use these endpoints:

```typescript
const API_BASE = 'http://localhost:8000';

// Create session
const response = await fetch(`${API_BASE}/api/session/create`, {
  method: 'POST'
});
const { session_id } = await response.json();

// Set gender
await fetch(`${API_BASE}/api/session/${session_id}/gender`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ gender: 'female' })
});

// Upload images
const formData = new FormData();
files.forEach(file => formData.append('files', file));
await fetch(`${API_BASE}/api/session/${session_id}/upload`, {
  method: 'POST',
  body: formData
});

// Generate embeddings
await fetch(`${API_BASE}/api/session/${session_id}/embed`, {
  method: 'POST'
});

// Generate outfits
const outfits = await fetch(`${API_BASE}/api/session/${session_id}/generate`, {
  method: 'POST'
}).then(r => r.json());
```

## Testing

```bash
# Run basic API tests
cd /Users/tuantran/Downloads/CVML/backend
python3 api/test_api.py
```

## Notes

- **Embedding service**: Requires CLIP model. If not installed, image upload endpoints will return 503.
- **Session cleanup**: Sessions persist until explicitly deleted or server is manually cleaned.
- **Anti-repeat**: Maintains memory of shown items across generations within a session.
- **State evolution**: Alpha/beta/pref values evolve based on user feedback.
