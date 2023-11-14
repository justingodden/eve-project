from datetime import datetime
import pathlib


class Cleaner:
    def __init__(self):
        pass

    @staticmethod
    def clean_published_time(published_time: str) -> datetime:
        return datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%S.%f%z")

    @staticmethod
    def clean_content(content: str) -> str:
        return "\n".join(content)

    @staticmethod
    def extract_image_filename(image_url: str) -> str:
        return pathlib.Path(image_url).name
