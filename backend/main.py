from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import json
from pathlib import Path

app = FastAPI(title="Candidate Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data
DATA_FILE = Path(__file__).parent.parent / "mock-data" / "candidates.json"

def load_candidates():
    """Load candidates from JSON file"""
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return data["candidates"]


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Candidate Management API", "docs": "/docs"}

@app.get("/api/sources")
def get_sources():
    candidates = load_candidates()
    sources = sorted({c["source"] for c in candidates})
    return {"sources": sources}

@app.get("/api/application_type")
def get_sources():
    candidates = load_candidates()
    application_type = sorted({c["application_type"] for c in candidates})
    return {"application_type": application_type}


@app.get("/api/candidates")
def get_candidates(
    # Search
    search: Optional[str] = Query(None, description="Search by name, position, or company"),

    # Multi-filtering
    application_type: Optional[List[str]] = Query(None, description="Filter by application type"),
    source: Optional[List[str]] = Query(None, description="Filter by source"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),

    # Sorting
    sort_by: Optional[str] = Query("last_activity", description="Sort by: last_activity | name"),
    sort_order: Optional[str] = Query("desc", description="Order: asc | desc"),

    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(5, ge=1, le=50, description="Items per page"),
):
    """
    Candidate List API with:
    - Search
    - Multi-filtering
    - Sorting
    - Pagination
    - Clean response structure
    """

    # ---------------------------------------------------
    # Load data
    # ---------------------------------------------------
    candidates = load_candidates()

    # ---------------------------------------------------
    # Search Filter
    # ---------------------------------------------------
    if search:
        term = search.lower()
        candidates = [
            c for c in candidates
            if term in c["name"].lower()
            or term in c["position"].lower()
            or term in c["company"].lower()
        ]

    # ---------------------------------------------------
    # Multi-Filter: application_type
    # ---------------------------------------------------
    if application_type:
        candidates = [
            c for c in candidates if c["application_type"] in application_type
        ]
    print("application_type: ",application_type)
    # ---------------------------------------------------
    # Multi-Filter: source
    # ---------------------------------------------------
    if source:
        candidates = [
            c for c in candidates if c["source"] in source
        ]

    # ---------------------------------------------------
    # Multi-Filter: job_id
    # ---------------------------------------------------
    if job_id:
        candidates = [
            c for c in candidates if c["job_id"] == job_id
        ]

    # ---------------------------------------------------
    # Sorting
    # ---------------------------------------------------
    reverse = sort_order == "desc"

    if sort_by == "last_activity":
        candidates = sorted(candidates, key=lambda c: c["last_activity"], reverse=reverse)

    if sort_by == "name":
        candidates = sorted(candidates, key=lambda c: c["name"].lower(), reverse=reverse)

    # ---------------------------------------------------
    # Pagination
    # ---------------------------------------------------
    total = len(candidates)
    start = (page - 1) * per_page
    end = start + per_page

    paginated = candidates[start:end]
    total_pages = max((total + per_page - 1) // per_page, 1)

    # ---------------------------------------------------
    # Better Response Structure
    # ---------------------------------------------------
    return {
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "filters": {
                "search": search,
                "application_type": application_type,
                "source": source,
                "job_id": job_id,
            }
        },
        "data": paginated
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
