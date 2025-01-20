from manga_ocr import MangaOcr
import PIL.Image

class OCR:
    def __init__(self):
        self.mocr = MangaOcr()

    def extract_text(self, image):
        """Extract text from an image using MangaOCR."""
        # If the input is a file path, open it as a PIL.Image
        if isinstance(image, str):
            img = PIL.Image.open(image)
        elif isinstance(image, PIL.Image.Image):
            img = image
        else:
            raise ValueError("Invalid input type for extract_text. Expected str or PIL.Image.")

        # Perform OCR
        text = self.mocr(img)
        return text
