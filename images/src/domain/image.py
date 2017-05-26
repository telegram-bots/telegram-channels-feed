from io import BytesIO
from typing import Optional


class Image:
    def __init__(self, mime: Optional[str], content: Optional[bytes]):
        self.mime = mime
        self.content = BytesIO(content) if content is not None else None

    def is_empty(self) -> bool:
        return self.mime is None or self.content is None

    def __str__(self):
        return f"Image {self.mime} {len(self.content)}"
