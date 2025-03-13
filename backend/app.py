import os
import sys
import csv
import io
import base64
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import tensorflow as tf
# Import our existing manga translation modules
from ocr import OCR
from image_processing.text_segmentation import TextSegmentation
from image_processing.text_bounding import TextBounding
from translation.deepl import translate_deepl
from typesetting import overlay_translated_text

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create required directories
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
UPLOAD_DIR = os.path.join(OUTPUT_DIR, "uploads")
INPAINTED_DIR = os.path.join(OUTPUT_DIR, "inpainted")
TEXT_ONLY_DIR = os.path.join(OUTPUT_DIR, "text_only")
BOXED_DIR = os.path.join(OUTPUT_DIR, "boxed")
TRANSLATED_DIR = os.path.join(OUTPUT_DIR, "translated")
CSV_DIR = os.path.join(OUTPUT_DIR, "csv")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INPAINTED_DIR, exist_ok=True)
os.makedirs(TEXT_ONLY_DIR, exist_ok=True)
os.makedirs(BOXED_DIR, exist_ok=True)
os.makedirs(TRANSLATED_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# Upload manga image endpoint
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    # Generate unique filename
    original_filename = image_file.filename
    file_ext = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    upload_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the uploaded image
    image_file.save(upload_path)
    
    return jsonify({
        'message': 'Image uploaded successfully',
        'image_id': os.path.splitext(unique_filename)[0],
        'original_filename': original_filename
    })
    
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
            
def display_translated_image(img_path):
    img = Image.open(img_path)
    img.show()

# Process manga image endpoint
@app.route('/api/process/<image_id>', methods=['POST'])
def process_image(image_id):
    # Locate the image
    for ext in ['.jpg', '.jpeg', '.png']:
        img_path = os.path.join(UPLOAD_DIR, f"{image_id}{ext}")
        if os.path.exists(img_path):
            break
    else:
        return jsonify({'error': 'Image not found'}), 404
    
    # Check if this image has already been processed
    translated_img_path = os.path.join(TRANSLATED_DIR, f"{image_id}_translated.png")
    csv_file_path = os.path.join(CSV_DIR, f"{image_id}_translations.csv")
    
    # If both the translated image and CSV file exist, the image has been processed before
    if os.path.exists(translated_img_path) and os.path.exists(csv_file_path):
        # Read existing translations from CSV
        translations = []
        with open(csv_file_path, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if len(row) >= 6:  # Ensure we have enough columns
                    translations.append({
                        'id': i,
                        'original_text': row[0],
                        'translated_text': row[1],
                        'bbox': [int(row[2]), int(row[3]), int(row[4]), int(row[5])]
                    })
        
        # Find existing files
        inpainted_files = [f for f in os.listdir(INPAINTED_DIR) if f.startswith(image_id)]
        text_only_files = [f for f in os.listdir(TEXT_ONLY_DIR) if f.startswith(image_id)]
        boxed_files = [f for f in os.listdir(BOXED_DIR) if f.startswith(image_id)]
        
        # Return paths to existing processed files
        return jsonify({
            'message': 'Image already processed',
            'original_image': f"/api/images/uploads/{os.path.basename(img_path)}",
            'inpainted_image': f"/api/images/inpainted/{inpainted_files[0]}" if inpainted_files else "",
            'text_only_image': f"/api/images/text_only/{text_only_files[0]}" if text_only_files else "",
            'boxed_image': f"/api/images/boxed/{boxed_files[0]}" if boxed_files else "",
            'translated_image': f"/api/images/translated/{image_id}_translated.png",
            'translations': translations,
            'redirect_url': f"/view/{image_id}"
        })
    
    try:
        # Initialize the TextSegmentation class
        segmenter = TextSegmentation()

        # Process the image
        inpainted_path, text_only_path = segmenter.segmentPage(img_path, INPAINTED_DIR, TEXT_ONLY_DIR)

        # Initialize the TextBounding class 
        text_bounding = TextBounding()

        # Process the text-only image for OCR bounding
        ocr_results = text_bounding.process_text_regions(text_only_path)

        # Draw and save boxes around detected text regions  
        boxed_image_path = text_bounding.draw_boxes(text_only_path, BOXED_DIR)

        # Define the CSV output path
        output_csv_file = os.path.join(CSV_DIR, f"{image_id}_translations.csv")
        
        # Process translations and save to CSV
        bounding_boxes = text_bounding.detect_text_regions(text_only_path)
        process_translation_to_csv(output_csv_file, ocr_results, bounding_boxes)
        
        # Read the translations we just created
        translations = []
        with open(output_csv_file, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if len(row) >= 6:  # Ensure we have enough columns
                    translations.append({
                        'id': i,
                        'original_text': row[0],
                        'translated_text': row[1],
                        'bbox': [int(row[2]), int(row[3]), int(row[4]), int(row[5])]
                    })
        
        # Overlay translations on the inpainted image
        translated_img_path = os.path.join(TRANSLATED_DIR, f"{image_id}_translated.png")
        overlay_translated_text(inpainted_path, output_csv_file, translated_img_path)
        
        # Return response with paths to all processed images
        return jsonify({
            'message': 'Image processed successfully',
            'original_image': f"/api/images/uploads/{os.path.basename(img_path)}",
            'inpainted_image': f"/api/images/inpainted/{os.path.basename(inpainted_path)}",
            'text_only_image': f"/api/images/text_only/{os.path.basename(text_only_path)}",
            'boxed_image': f"/api/images/boxed/{os.path.basename(boxed_image_path)}",
            'translated_image': f"/api/images/translated/{image_id}_translated.png",
            'translations': translations,
            'redirect_url': f"/view/{image_id}"
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

# Update translation endpoint
@app.route('/api/translations/<image_id>', methods=['PATCH'])
def update_translations(image_id):
    data = request.json
    if not data or 'translations' not in data:
        return jsonify({'error': 'No translation data provided'}), 400
    
    csv_file_path = os.path.join(CSV_DIR, f"{image_id}_translations.csv")
    if not os.path.exists(csv_file_path):
        return jsonify({'error': 'Translation data not found'}), 404
    
    try:
        # Read existing translations
        translations = []
        with open(csv_file_path, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            translations = list(reader)
        
        # Update translations from the request
        for trans in data['translations']:
            idx = trans.get('id')
            if idx is not None and 0 <= idx < len(translations):
                translations[idx][1] = trans.get('translated_text', translations[idx][1])
        
        # Write back to CSV
        with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Original Text", "Translated Text", "x", "y", "w", "h"])
            writer.writerows(translations)
        
        # Find the inpainted image
        inpainted_files = [f for f in os.listdir(INPAINTED_DIR) if f.startswith(image_id)]
        if not inpainted_files:
            return jsonify({'error': 'Inpainted image not found'}), 404
        
        inpainted_path = os.path.join(INPAINTED_DIR, inpainted_files[0])
        
        # Re-overlay translations on the inpainted image
        translated_img_path = os.path.join(TRANSLATED_DIR, f"{image_id}_translated.png")
        overlay_translated_text(inpainted_path, csv_file_path, translated_img_path)
        
        return jsonify({
            'message': 'Translations updated successfully',
            'translated_image': f"/api/images/translated/{image_id}_translated.png"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve images endpoints
@app.route('/api/images/<path:image_type>/<filename>', methods=['GET'])
def serve_image(image_type, filename):
    image_dirs = {
        'uploads': UPLOAD_DIR,
        'inpainted': INPAINTED_DIR,
        'text_only': TEXT_ONLY_DIR,
        'boxed': BOXED_DIR,
        'translated': TRANSLATED_DIR
    }
    
    if image_type not in image_dirs:
        return jsonify({'error': 'Invalid image type'}), 400
    
    image_path = os.path.join(image_dirs[image_type], filename)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    
    # Read the image file and convert to base64
    with open(image_path, 'rb') as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Get image mimetype based on extension
    ext = os.path.splitext(filename)[1].lower()
    mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
    
    return jsonify({
        'data': f"data:{mime_type};base64,{encoded_img}"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 