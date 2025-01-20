import os
import sys
import csv
import cv2
from PIL import Image
from ocr import OCR
from image_processing.text_segmentation import TextSegmentation
from image_processing.text_bounding import TextBounding
from translation.deepl import translate_deepl
from typesetting import overlay_translated_text
from textline_merge import Quadrilateral, merge_bboxes_text_region, TextBlock

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def process_translation_to_csv(csv_file_path, text_blocks, original_image_path):
    # Replace the CSV file if it already exists
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Original Text", "Translated Text", "x", "y", "w", "h"])

    # Initialize OCR
    ocr = OCR()

    # Open the original image
    original_image = Image.open(original_image_path)

    # Process each text block for OCR and translation
    with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for block in text_blocks:
            for line_pts in block.lines:
                # Calculate bounding box for the line
                x_coords = [pt[0] for pt in line_pts]
                y_coords = [pt[1] for pt in line_pts]
                x, y, w, h = min(x_coords), min(y_coords), max(x_coords) - min(x_coords), max(y_coords) - min(y_coords)

                # Skip invalid bounding boxes
                if w <= 0 or h <= 0:
                    print(f"Skipping invalid bounding box: x={x}, y={y}, w={w}, h={h}")
                    continue

                # Crop the region from the original image
                cropped_image = original_image.crop((x, y, x + w, y + h))
                cropped_image_path = "temp_cropped_image.png"
                cropped_image.save(cropped_image_path)

                # Extract text using OCR
                original_text = ocr.extract_text(cropped_image_path)

                # Translate the text using DeepL
                translated_text = translate_deepl(original_text)

                # Write the original and translated text, and bounding box to the CSV file
                writer.writerow([original_text, str(translated_text), x, y, w, h])
                print(f"Processed and added translation for bounding box {x}, {y}, {w}, {h} to CSV.")

    # Clean up the temporary cropped image
    if os.path.exists("temp_cropped_image.png"):
        os.remove("temp_cropped_image.png")


def main(img_path):
    # Define paths
    image_name = os.path.splitext(os.path.basename(img_path))[0]
    output_inpainted_dir = "output/inpainted/"
    output_text_only_dir = "output/text_only/"
    output_ocr_dir = "output/ocr/"
    output_boxed_dir = "output/boxed/"
    output_csv_file = f"output/{image_name}_translations.csv"
    output_text_overlay_path = f"output/{image_name}_translated.png"

    # Ensure output directories exist
    os.makedirs(output_inpainted_dir, exist_ok=True)
    os.makedirs(output_text_only_dir, exist_ok=True)
    os.makedirs(output_ocr_dir, exist_ok=True)
    os.makedirs(output_boxed_dir, exist_ok=True)

    # Initialize the TextSegmentation class
    segmenter = TextSegmentation()

    # Process the image
    inpainted_path, text_only_path = segmenter.segmentPage(img_path, output_inpainted_dir, output_text_only_dir)

    # Get image dimensions
    img = cv2.imread(text_only_path)
    height, width = img.shape[:2]  # Extract height and width

    # Initialize the TextBounding class
    text_bounding = TextBounding()

    # Detect text regions and their bounding boxes
    bounding_boxes = text_bounding.detect_text_regions(text_only_path)

    # Convert bounding boxes to Quadrilateral objects
    quadrilaterals = [
        Quadrilateral(
            pts=[
                (box[0], box[1]),  # Top-left corner
                (box[0] + box[2], box[1]),  # Top-right corner
                (box[0] + box[2], box[1] + box[3]),  # Bottom-right corner
                (box[0], box[1] + box[3]),  # Bottom-left corner
            ],
            font_size=max(box[3], 12),  # Use height as a proxy for font size, with a minimum of 12
            angle=0,  # Default angle
            centroid=(box[0] + box[2] / 2, box[1] + box[3] / 2),  # Compute the centroid
            fg_color=(0, 0, 0),  # Default to black
            bg_color=(255, 255, 255),  # Default to white
            text="",  # Placeholder for now
            prob=1.0  # Default probability
        )
        for box in bounding_boxes
    ]

    # Merge bounding boxes into text regions
    text_blocks = list(merge_bboxes_text_region(quadrilaterals, width=width, height=height))

    # Process translations and save to CSV
    process_translation_to_csv(output_csv_file, text_blocks, img_path)

    # Overlay translations on the inpainted image
    overlay_translated_text(inpainted_path, output_csv_file, output_text_overlay_path, font_path="path/to/arial.ttf")

    # Print results
    print("\n--- Segmentation Results ---")
    print(f"Inpainted Image: {inpainted_path}")
    print(f"Text-Only Image: {text_only_path}")
    print("\n--- OCR and Translation Results ---")
    print(f"Translations saved to: {output_csv_file}")
    print(f"Translated Image Saved to: {output_text_overlay_path}")


if __name__ == "__main__":
    img_path = "test_panels/mushoku21.jpg"
    main(img_path)
