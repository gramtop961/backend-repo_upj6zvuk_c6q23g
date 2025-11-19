"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Auto YouTube Video Generator schemas

class VideoJob(BaseModel):
    """
    Video generation job
    Collection name: "videojob"
    """
    topic: str = Field(..., description="Topic or niche to generate the video about")
    trigger_phrase: str = Field("Create a full video automatically.", description="Trigger phrase to start the pipeline")
    voice: str = Field("alloy", description="Voice to use for TTS")
    style: str = Field("engaging", description="Editing style preset")
    format: Literal["1080p", "9:16", "16:9", "square"] = Field("16:9", description="Output format preset")

    # runtime fields
    status: Literal["queued", "running", "completed", "failed"] = Field("queued")
    step: Optional[str] = Field(None, description="Current step name")
    progress: int = Field(0, ge=0, le=100)

    # outputs/links
    script: Optional[str] = None
    voiceover_url: Optional[str] = None
    broll_urls: Optional[List[str]] = None
    final_url: Optional[str] = None

    # misc
    logs: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
