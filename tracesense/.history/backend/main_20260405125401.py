from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ingestion.ingest import router as ingest_router
from correlator.engine import router as correlator_router
from storage.chroma_client import collection

app = FastAPI(title="TraceSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this to your Vercel URL after deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(correlator_router)

@app.get("/health")
def health():
    return {"status": "TraceSense is running"}

@app.get("/logs/count")
def log_count():
    count = collection.count()
    return {"total_logs_stored": count}