from google.cloud import vision
from .vision_types import RecognisedText


class VisionTransport:
    def __init__(self, cloud_credentials_path):
        self.__client = vision.ImageAnnotatorClient.from_service_account_json(
                            cloud_credentials_path
                        )

    def recognize_bytes(self, bytes):
        image = vision.types.Image(content=bytes)
        response = self.__client.text_detection(image=image)
        result = []
        for text in response.text_annotations:
            result.append(RecognisedText(
                text.description,
                text.bounding_poly.vertices
            ))
        return result
