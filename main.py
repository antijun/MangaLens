import os
import sys
from image_processing.text_segmentation import TextSegmentation
from image_processing.text_bounding import TextBounding
from ocr import OCR

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Define paths
    image_path = "test_panels/mushoku2.jpg"
    output_inpainted_dir = "output/inpainted/"
    output_text_only_dir = "output/text_only/"
    output_ocr_dir = "output/ocr/"
    output_text_dir = "output/extracted_text/"
    output_boxed_dir = "output/boxed/"

    # Ensure output directories exist
    os.makedirs(output_inpainted_dir, exist_ok=True)
    os.makedirs(output_text_only_dir, exist_ok=True)
    os.makedirs(output_ocr_dir, exist_ok=True)
    os.makedirs(output_text_dir, exist_ok=True)
    os.makedirs(output_boxed_dir, exist_ok=True)

    # Initialize the TextSegmentation class
    segmenter = TextSegmentation()

    # Process the image
    inpainted_path, text_only_path = segmenter.segmentPage(image_path, output_inpainted_dir, output_text_only_dir)

    # Initialize the TextBounding class
    text_bounding = TextBounding()

    # Process the text-only image for OCR bounding
    ocr_results = text_bounding.process_text_regions(text_only_path, output_ocr_dir)

    # Initialize OCR
    ocr = OCR()

    # Process each cropped region with OCR
    for i, ocr_file in enumerate(ocr_results):
        text = ocr.extract_text(ocr_file, output_text_dir)
        print(f"Extracted text for region {i + 1} saved to {os.path.join(output_text_dir, f'region_{i + 1}_text.txt')}")

    # Draw and save boxes around detected text regions
    text_bounding.draw_boxes(text_only_path, output_boxed_dir)

    # Print results
    print("\n--- Segmentation Results ---")
    print(f"Inpainted Image: {inpainted_path}")
    print(f"Text-Only Image: {text_only_path}")
    print("\n--- OCR Results ---")
    for i, ocr_file in enumerate(ocr_results):
        print(f"OCR Region {i + 1}: {ocr_file}")

if __name__ == "__main__":
    main()