import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="Interior Design Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Models (mirror of schemas.py minimal for typing) -----
class InquiryIn(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    project_type: Optional[str] = None
    budget: Optional[str] = None
    message: str


# ----- Basic health -----
@app.get("/")
def read_root():
    return {"message": "Interior Design API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"

    # Env flags
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ----- Portfolio Endpoints -----
@app.get("/api/projects")
def list_projects(category: Optional[str] = None):
    """Return portfolio projects. Optionally filter by category."""
    if db is None:
        # If DB not configured, return empty list to keep frontend stable
        return []
    filt = {}
    if category:
        filt["category"] = category
    docs = get_documents("project", filt)
    # Convert ObjectId and nested structures to JSON-friendly
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
    return docs


@app.get("/api/projects/{slug}")
def get_project(slug: str):
    if db is None:
        raise HTTPException(status_code=404, detail="Project not found")
    docs = get_documents("project", {"slug": slug}, limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Project not found")
    doc = docs[0]
    doc["id"] = str(doc.pop("_id", ""))
    return doc


# ----- Inquiry Endpoint -----
@app.post("/api/inquiries")
def create_inquiry(inquiry: InquiryIn):
    if db is None:
        # Accept but indicate non-persistent environment
        return {"status": "accepted", "message": "Database not configured; inquiry not persisted."}
    inserted_id = create_document("inquiry", inquiry.model_dump())
    return {"status": "ok", "id": inserted_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
