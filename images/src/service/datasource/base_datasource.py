from abc import ABC, abstractmethod

from ...domain import Image


class BaseDataSource(ABC):
    @abstractmethod
    def get(self, img_id: str) -> Image:
        pass

    @abstractmethod
    def store(self, img_id: str, content: bytes):
        pass
