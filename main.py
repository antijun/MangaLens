import os
import sys
import csv
import io 
import numpy as np
from ocr import OCR
from PIL import Image
from image_processing.text_segmentation import TextSegmentation
from image_processing.text_bounding import TextBounding
from translation.deepl import translate_deepl
from typesetting import overlay_translated_text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def display_translated_image(img_path):
    img = Image.open(img_path)
    img.show()

def process_translation_to_csv(csv_file_path, ocr_results, bounding_boxes):
    # Replace the CSV file if it already exists
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Original Text", "Translated Text", "x", "y", "w", "h"])

    # Initialize OCR
    ocr = OCR()

    # Process each cropped region for OCR and translation
    with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for ocr_image, (x, y, w, h) in zip(ocr_results, bounding_boxes):
            # Skip invalid bounding boxes
            if w <= 0 or h <= 0:
                print(f"Skipping invalid bounding box: x={x}, y={y}, w={w}, h={h}")
                continue

            # Convert numpy.ndarray to PIL.Image
            if isinstance(ocr_image, np.ndarray):
                ocr_image = Image.fromarray(ocr_image)

            # Extract text using OCR
            original_text = ocr.extract_text(ocr_image)

            # Translate the text using DeepL
            translated_text = translate_deepl(original_text)

            # Write the original and translated text, and bounding box to the CSV file
            writer.writerow([original_text, str(translated_text), x, y, w, h])
            print(f"Processed and added translation for bounding box {x}, {y}, {w}, {h} to CSV.")

def main(img_path):
    # Define paths
    image_name = os.path.splitext(os.path.basename(img_path))[0]
    output_inpainted_dir = "output/inpainted/"
    output_text_only_dir = "output/text_only/"
    output_boxed_dir = "output/boxed/"
    output_csv_file = f"output/{image_name}_translations.csv"
    output_text_overlay_path = f"output/{image_name}_translated.png"

    # Ensure output directories exist
    os.makedirs(output_inpainted_dir, exist_ok=True)
    os.makedirs(output_text_only_dir, exist_ok=True)
    os.makedirs(output_boxed_dir, exist_ok=True)

    # Initialize the TextSegmentation class
    segmenter = TextSegmentation()

    # Process the image
    inpainted_path, text_only_path = segmenter.segmentPage(img_path, output_inpainted_dir, output_text_only_dir)

    # Initialize the TextBounding class
    text_bounding = TextBounding()

    # Process the text-only image for OCR bounding
    ocr_results = text_bounding.process_text_regions(text_only_path)

    # Draw and save boxes around detected text regions
    text_bounding.draw_boxes(text_only_path, output_boxed_dir)

    # Process translations and save to CSV
    bounding_boxes = text_bounding.detect_text_regions(text_only_path)
    process_translation_to_csv(output_csv_file, ocr_results, bounding_boxes)

    # Overlay translations on the inpainted image
    overlay_translated_text(inpainted_path, output_csv_file, output_text_overlay_path, font_path="path/to/arial.ttf")

    # Print results
    print("\n--- Segmentation Results ---")
    print(f"Inpainted Image: {inpainted_path}")
    print(f"Text-Only Image: {text_only_path}")
    print("\n--- OCR and Translation Results ---")
    print(f"Translations saved to: {output_csv_file}")
    print(f"Translated Image Saved to: {output_text_overlay_path}")
    
    display_translated_image(output_text_overlay_path)
    
if __name__ == "__main__":
    img_path = "test_panels/mushoku3.jpg"
    main(img_path)