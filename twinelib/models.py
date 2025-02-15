from pydantic import BaseModel
from typing import List, Optional

class Passage(BaseModel):
    pid: int
    name: str
    tags: Optional[str] = ""
    position: str  # e.g. "175,75"
    size: str      # e.g. "100,100"
    content: str

class Story(BaseModel):
    name: str
    startnode: int
    creator: str = "Twine"
    creator_version: str = "2.10.0"
    format: str = "Harlowe"
    format_version: str = "3.3.9"
    ifid: Optional[str] = None
    options: str = "debug"
    tags: str = ""
    zoom: str = "1"
    hidden: Optional[str] = None
    passages: List[Passage]
