import os
from os.path import abspath, dirname
import shutil
from urllib3.response import HTTPResponse


class Uploader:
    def __init__(self, local: bool = True):
        self.local = local

    def save_local(self, image_data: HTTPResponse, image_filename: str) -> None:
        folder = os.path.join(abspath(dirname(dirname(__file__))), "images")
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, image_filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(image_data, f)

    def save_s3(self, image_data: HTTPResponse, image_filename: str) -> None:
        raise NotImplementedError

    def save_image(self, image_data: HTTPResponse, image_filename: str) -> None:
        if self.local:
            self.save_local(image_data, image_filename)
        else:
            self.save_s3(image_data, image_filename)
