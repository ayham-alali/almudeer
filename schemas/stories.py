from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class StoryBase(BaseModel):
    title: Optional[str] = None
    type: str # text, image, video, voice, audio, file

class StoryCreateText(StoryBase):
    content: str
    type: str = "text"

class StoryResponse(StoryBase):
    id: int
    user_id: Optional[str]
    content: Optional[str]
    media_path: Optional[str]
    thumbnail_path: Optional[str]
    duration_ms: int
    created_at: datetime
    is_viewed: bool = False

    class Config:
        from_attributes = True

class StoryViewerDetails(BaseModel):
    viewer_contact: str
    viewer_name: Optional[str]
    viewed_at: datetime

class StoriesListResponse(BaseModel):
    success: bool
    stories: List[StoryResponse]
