import os
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding, SparseTextEmbedding

class QdrantDB:  # Renamed from LocalQdrantDB since it's not always local now
    def __init__(self):
        # 1. Configuration via Environment Variables
        # If running in Docker Compose, this will be "http://qdrant:6333"
        # If running locally, defaults to "http://localhost:6333" or local path
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        print(f"Connecting to Qdrant at: {self.qdrant_url}")
        
        # Initialize Client
        self.client = QdrantClient(url=self.qdrant_url)
        
        self.JOBS_COLLECTION = "jobs_collection"
        self.CANDIDATES_COLLECTION = "candidates_collection"

        print("Loading AI Models... (This happens only once)")
        # FastEmbed will download models to a cache directory inside the container
        self.dense_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.sparse_model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")
        
        self._init_collection(self.JOBS_COLLECTION)
        self._init_collection(self.CANDIDATES_COLLECTION)

    def _init_collection(self, collection_name: str):
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": models.VectorParams(
                        size=384,
                        distance=models.Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=True)
                    )
                }
            )
            print(f"Created collection: {collection_name}")

    def _get_dense_embedding(self, text: str) -> List[float]:
        embedding = list(self.dense_model.embed([text]))[0]
        return embedding.tolist()

    def _get_sparse_embedding(self, text: str) -> models.SparseVector:
        sparse_vec = list(self.sparse_model.embed([text]))[0]
        return models.SparseVector(
            indices=sparse_vec.indices.tolist(),
            values=sparse_vec.values.tolist()
        )

    # --- JOB METHODS ---
    def upsert_job(self, job_id: uuid.UUID, title: str, description: str, skills: List[str], extra_payload: Dict[str, Any]):
        rich_text = f"Job Title: {title}. Skills: {', '.join(skills)}. Description: {description}"
        self._upsert(self.JOBS_COLLECTION, str(job_id), rich_text, {
            "job_id": str(job_id), "title": title, "skills": skills, **extra_payload
        })

    def search_jobs(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._search(self.JOBS_COLLECTION, query_text, limit)

    def delete_job(self, job_id: uuid.UUID):
        self._delete(self.JOBS_COLLECTION, str(job_id))

    # --- CANDIDATE METHODS ---
    def upsert_candidate(self, candidate_id: uuid.UUID, skills: List[str], experience_years: int, roles: List[str], locations: List[str]):
        rich_text = (
            f"Skills: {', '.join(skills)}. "
            f"Experience: {experience_years} years. "
            f"Preferred Roles: {', '.join(roles)}. "
            f"Preferred Locations: {', '.join(locations)}."
        )
        self._upsert(self.CANDIDATES_COLLECTION, str(candidate_id), rich_text, {
            "candidate_id": str(candidate_id), "skills": skills, 
            "experience_years": experience_years, "roles": roles, "locations": locations
        })

    def search_candidates(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._search(self.CANDIDATES_COLLECTION, query_text, limit)

    def delete_candidate(self, candidate_id: uuid.UUID):
        self._delete(self.CANDIDATES_COLLECTION, str(candidate_id))

    # --- HELPERS ---
    def _upsert(self, collection_name: str, point_id: str, text: str, payload: Dict[str, Any]):
        dense_vec = self._get_dense_embedding(text)
        sparse_vec = self._get_sparse_embedding(text)
        self.client.upsert(
            collection_name=collection_name,
            points=[models.PointStruct(id=point_id, vector={"dense": dense_vec, "sparse": sparse_vec}, payload=payload)]
        )

    def _delete(self, collection_name: str, point_id: str):
        self.client.delete(collection_name=collection_name, points_selector=[point_id])

    def _search(self, collection_name: str, query_text: str, limit: int) -> List[Dict[str, Any]]:
        dense_query = self._get_dense_embedding(query_text)
        sparse_query = self._get_sparse_embedding(query_text)
        
        results = self.client.query_points(
            collection_name=collection_name,
            prefetch=[
                models.Prefetch(query=sparse_query, using="sparse", limit=limit * 2),
                models.Prefetch(query=dense_query, using="dense", limit=limit * 2),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit
        )

        matches: List[Dict[str, Any]] = []
        for hit in results.points:
            payload = hit.payload if hit.payload is not None else {}
            match_data = payload.copy()
            match_data["match_score"] = hit.score
            matches.append(match_data)
        return matches

# --- WRAPPERS ---
vector_db = QdrantDB()

def upsert_job_embedding(job_id: uuid.UUID, title: str, description: str, skills: List[str], extra_payload: Dict[str, Any]):
    vector_db.upsert_job(job_id, title, description, skills, extra_payload)
def delete_job_embedding(job_id: uuid.UUID):
    vector_db.delete_job(job_id)
def search_jobs_by_vector(query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
    return vector_db.search_jobs(query_text, limit)
def upsert_candidate_embedding(candidate_id: uuid.UUID, skills: List[str], experience_years: int, roles: List[str], locations: List[str]):
    vector_db.upsert_candidate(candidate_id, skills, experience_years, roles, locations)
def search_candidates_by_vector(query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
    return vector_db.search_candidates(query_text, limit)