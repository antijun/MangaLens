import os
import sys
import csv
from image_processing.text_segmentation import TextSegmentation
from image_processing.text_bounding import TextBounding
from ocr import OCR
from translation.deepl import translate_deepl

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def process_translation_to_csv(csv_file_path, ocr_results):
    # Replace the CSV file if it already exists
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Original Text", "Translated Text"])

    # Initialize OCR
    ocr = OCR()

    # Process each cropped region for OCR and translation
    with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for ocr_file in ocr_results:
            # Extract text using OCR
            original_text = ocr.extract_text(ocr_file)

            # Translate the text using DeepL
            translated_text = translate_deepl(original_text)

            # Write the original and translated text to the CSV file
            writer.writerow([original_text, str(translated_text)])
            print(f"Processed and added translation for {ocr_file} to CSV.")

def main(img_path):
    # Define paths
    image_name = os.path.splitext(os.path.basename(img_path))[0]
    output_inpainted_dir = "output/inpainted/"
    output_text_only_dir = "output/text_only/"
    output_ocr_dir = "output/ocr/"
    output_boxed_dir = "output/boxed/"
    output_csv_file = f"output/{image_name}_translations.csv"

    # Ensure output directories exist
    os.makedirs(output_inpainted_dir, exist_ok=True)
    os.makedirs(output_text_only_dir, exist_ok=True)
    os.makedirs(output_ocr_dir, exist_ok=True)
    os.makedirs(output_boxed_dir, exist_ok=True)

    # Initialize the TextSegmentation class
    segmenter = TextSegmentation()

    # Process the image
    inpainted_path, text_only_path = segmenter.segmentPage(img_path, output_inpainted_dir, output_text_only_dir)

    # Initialize the TextBounding class
    text_bounding = TextBounding()

    # Process the text-only image for OCR bounding
    ocr_results = text_bounding.process_text_regions(text_only_path, output_ocr_dir)

    # Draw and save boxes around detected text regions
    text_bounding.draw_boxes(text_only_path, output_boxed_dir)

    # Process translations and save to CSV
    process_translation_to_csv(output_csv_file, ocr_results)

    # Print results
    print("\n--- Segmentation Results ---")
    print(f"Inpainted Image: {inpainted_path}")
    print(f"Text-Only Image: {text_only_path}")
    print("\n--- OCR and Translation Results ---")
    print(f"Translations saved to: {output_csv_file}")

if __name__ == "__main__":
    img_path = "test_panels/mushoku2.jpg"
    main(img_path)