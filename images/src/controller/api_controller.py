from flask import send_file
from flask.views import MethodView

from ..service import ImageRetriever


class APIController(MethodView):
    retriever = ImageRetriever()

    def get(self, img_id: str):
        image = self.retriever.retrieve(img_id)
        return send_file(image.content, mimetype=image.mime)
