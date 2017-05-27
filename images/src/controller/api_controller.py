from flask import send_from_directory
from flask.views import MethodView

from src.config import image_retriever


class APIController(MethodView):
    def get(self, path):
        storage_path, file_name = image_retriever.retrieve(path)
        return send_from_directory(storage_path, file_name)
