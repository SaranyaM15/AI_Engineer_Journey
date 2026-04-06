from fastapi import APIRouter
from pydantic import BaseModel
from storage.chroma_client import collection
from embeddings.embeddings import embed_text
from datetime import datetime

router = APIRouter()

TIME_WINDOW_SECONDS = 30

class CorrelateRequest(BaseModel):
    message: str
    timestamp: str

def temporal_score(query_ts: str, candidate_ts: str) -> float:
    try:
        t1 = datetime.fromisoformat(query_ts)
        t2 = datetime.fromisoformat(candidate_ts)
        diff = abs((t1 - t2).total_seconds())
        return round(max(0.0, 1.0 - (diff / TIME_WINDOW_SECONDS)), 4)
    except:
        return 0.5

@router.post("/correlate")
def correlate(req: CorrelateRequest):

    # Step 1 — embed the query
    query_vector = embed_text(req.message)

    # Step 2 — semantic search
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=20,
        include=["documents", "metadatas", "distances"]
    )

    candidates = []
    seen_services = set()

    for i in range(len(results["ids"][0])):
        meta      = results["metadatas"][0][i]
        message   = results["documents"][0][i]
        semantic  = round(1 - results["distances"][0][i], 4)
        temporal  = temporal_score(req.timestamp, meta["timestamp"])
        diversity = 0.1 if meta["service"] not in seen_services else 0.0
        seen_services.add(meta["service"])

        final = round(
            0.6 * semantic +
            0.3 * temporal +
            0.1 * diversity,
            4
        )

        candidates.append({
            "service":   meta["service"],
            "level":     meta["level"],
            "message":   message,
            "timestamp": meta["timestamp"],
            "scores": {
                "semantic": semantic,
                "temporal": temporal,
                "final":    final
            }
        })

    candidates.sort(key=lambda x: x["scores"]["final"], reverse=True)

    return {
        "query":            req.message,
        "incident_cluster": candidates[:7]
    }