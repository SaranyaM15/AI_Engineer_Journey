from fastapi import APIRouter
from pydantic import BaseModel
from storage.chroma_client import collection
from embeddings.embeddings import embed_text
import uuid

router = APIRouter()

class LogEntry(BaseModel):
    service: str
    level: str
    message: str
    timestamp: str

@router.post("/ingest")
def ingest_log(log: LogEntry):
    vector = embed_text(log.message)

    collection.add(
        ids=[str(uuid.uuid4())],
        embeddings=[vector],
        documents=[log.message],
        metadatas=[{
            "service":   log.service,
            "level":     log.level,
            "timestamp": log.timestamp
        }]
    )

    print(f"Ingested [{log.level}] [{log.service}] {log.message}")
    return {"status": "ingested"}