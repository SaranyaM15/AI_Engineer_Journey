import chromadb

client = chromadb.PersistentClient(path="./tracesense_db")

collection = client.get_or_create_collection(
    name="logs",
    metadata={"hnsw:space": "cosine"}
)