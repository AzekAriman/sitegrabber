
import csv
import os
import time
from typing import TextIO

class ManifestWriter:
    def __init__(self, path: str):
        self.path = path
        self._init_file()

    def _init_file(self):
        first = not os.path.exists(self.path)
        self.f: TextIO = open(self.path, "a", newline="", encoding="utf-8")
        self.w = csv.writer(self.f)
        if first:
            self.w.writerow([
                "timestamp", "page_url", "image_url", "local_path",
                "content_type", "size_bytes", "width", "height", "status"
            ])
            self.f.flush()

    def write(self, page_url: str, image_url: str, local_path: str,
              content_type: str, size_bytes: int, width: int, height: int, status: str):
        self.w.writerow([
            int(time.time()), page_url, image_url, local_path,
            content_type, size_bytes, width, height, status
        ])
        self.f.flush()

    def close(self):
        self.f.close()
