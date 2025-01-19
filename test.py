# from ocr.tesseract_ocr import extract_text
from ocr import extract_text
from translation.deepl import translate_deepl

text = extract_text('test_panels/00.jpg')

translation = translate_deepl(text)
print(translation)