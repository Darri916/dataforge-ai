from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, generate, quality, privacy, export
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="DataForge AI",
    description="Synthetic data generation with quality and privacy evaluation.",
    version="1.0.0"
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allows the React frontend (Vercel) to call this backend (Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://dataforge-ai-gold.vercel.app",
    "http://localhost:5173",],        
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(upload.router,   prefix="/api/upload",   tags=["Upload"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(quality.router,  prefix="/api/quality",  tags=["Quality"])
app.include_router(privacy.router,  prefix="/api/privacy",  tags=["Privacy"])
app.include_router(export.router,   prefix="/api/export",   tags=["Export"])

# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    logger.info("DataForge AI is running.")
    return {"status": "ok", "message": "DataForge AI backend is live."}