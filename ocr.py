from manga_ocr import MangaOcr
import os
import PIL

class OCR:
    def __init__(self):
        self.mocr = MangaOcr()

    def extract_text(self, image_path, output_path="output/"):
        """Extract text from an image using MangaOCR."""
        img = PIL.Image.open(image_path)
        text = self.mocr(img)

        text_file_path = os.path.join(output_path, f"{os.path.splitext(os.path.basename(image_path))[0]}_text.txt")
        with open(text_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        return text