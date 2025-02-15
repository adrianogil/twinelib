from pydantic import BaseModel, validator
from typing import List, Optional

class Passage(BaseModel):
    name: str
    content: str
    pid: Optional[int] = None
    tags: Optional[str] = ""
    position: Optional[str] = None
    size: Optional[str] = None

    @validator('content', pre=True)
    def parse_content(cls, value):
        # If the content is provided as a list, join the parts.
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and "choices" in item:
                    # Convert each choice into link syntax.
                    links = []
                    for choice_text, target in item["choices"].items():
                        links.append(f"[[{choice_text}->{target}]]")
                    parts.append("\n".join(links))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return value

class Story(BaseModel):
    name: str
    passages: List[Passage]
    startnode: Optional[int] = 1
