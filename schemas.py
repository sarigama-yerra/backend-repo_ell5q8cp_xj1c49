"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class Inquiry(BaseModel):
    """Client inquiry submissions
    Collection name: "inquiry"
    """
    name: str = Field(..., description="Client full name")
    email: str = Field(..., description="Client email address")
    phone: Optional[str] = Field(None, description="Phone number")
    project_type: Optional[str] = Field(None, description="Type of project e.g. Residential, Commercial")
    budget: Optional[str] = Field(None, description="Budget range text")
    message: str = Field(..., description="Inquiry message")


class ProjectImage(BaseModel):
    url: str
    caption: Optional[str] = None


class Project(BaseModel):
    """Portfolio projects
    Collection name: "project"
    """
    title: str = Field(..., description="Project title")
    slug: str = Field(..., description="URL-friendly unique slug")
    category: str = Field(..., description="Residential | Commercial | Renovation | Styling")
    location: Optional[str] = None
    cover_image: str = Field(..., description="Hero/cover image URL")
    summary: Optional[str] = None
    year: Optional[int] = None
    services: Optional[List[str]] = None
    gallery: Optional[List[ProjectImage]] = None
    before_after: Optional[List[ProjectImage]] = None
