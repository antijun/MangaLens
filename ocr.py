from manga_ocr import MangaOcr
import os
import PIL

class OCR:
    def __init__(self):
        self.mocr = MangaOcr()

    def extract_text(self, image_path):
        """Extract text from an image using MangaOCR."""
        img = PIL.Image.open(image_path)
        text = self.mocr(img)
        return text