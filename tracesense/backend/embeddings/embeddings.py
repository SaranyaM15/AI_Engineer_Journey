from sentence_transformers import SentenceTransformer

print("This is Loading SBERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("SBERT model loaded.")

def embed_text(text: str) -> list:
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()