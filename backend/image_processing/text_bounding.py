import os
import cv2
import tempfile
from tqdm import tqdm

class TextBounding:
    def __init__(self):
        pass

    def detect_text_regions(self, img_path, contour_size=0.01):
        """Detect text regions and return bounding boxes in manga reading order (right-to-left, top-to-bottom)."""
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge detection and thresholding
        edges = cv2.Sobel(gray, cv2.CV_8U, 1, 0)
        _, thresh = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations
        ele_size = (int(img.shape[0] * contour_size), int(img.shape[0] * contour_size))
        element = cv2.getStructuringElement(cv2.MORPH_RECT, ele_size)
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, element)

        # Find contours
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        noise_size_param = int(ele_size[0] / 3)
        contours = [cnt for cnt in contours if cnt.shape[0] > noise_size_param ** 2]

        # Bounding boxes
        bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]
        
        # Sort bounding boxes in manga reading order (right-to-left, top-to-bottom)
        # First, define manga panels by grouping text bubbles by rows
        row_height = sum([h for _, _, _, h in bounding_boxes]) / max(1, len(bounding_boxes))
        row_tolerance = row_height * 0.7  # Tolerance for grouping text in the same row
        
        # Group bounding boxes by row based on vertical position
        rows = {}
        for box in bounding_boxes:
            x, y, w, h = box
            # Find which row this box belongs to
            assigned = False
            for row_y in rows.keys():
                if abs(y - row_y) < row_tolerance:
                    rows[row_y].append(box)
                    assigned = True
                    break
            if not assigned:
                rows[y] = [box]
        
        # Sort rows by y-coordinate (top to bottom)
        sorted_rows = sorted(rows.items(), key=lambda item: item[0])
        
        # For each row, sort boxes from right to left
        manga_ordered_boxes = []
        for _, boxes in sorted_rows:
            # Sort boxes in this row from right to left
            right_to_left_boxes = sorted(boxes, key=lambda box: -box[0])  # Negative x to sort right-to-left
            manga_ordered_boxes.extend(right_to_left_boxes)
        
        return manga_ordered_boxes

    def crop_regions(self, img, bounding_boxes):
        """Crop bounding regions and return them as in-memory images."""
        cropped_images = []
        for (x, y, w, h) in bounding_boxes:
            cropped = img[y:y + h, x:x + w]
            cropped_images.append(cropped)
        return cropped_images

    def process_text_regions(self, img_path):
        """Detect and process text regions without saving cropped regions."""
        img = cv2.imread(img_path)
        bounding_boxes = self.detect_text_regions(img_path)
        cropped_images = self.crop_regions(img, bounding_boxes)
        return cropped_images

    def draw_boxes(self, img_path, output_dir):
        """Draw bounding boxes on the image and save it."""
        img = cv2.imread(img_path)
        bounding_boxes = self.detect_text_regions(img_path)

        for (x, y, w, h) in bounding_boxes:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        boxed_image_path = os.path.join(output_dir, os.path.basename(img_path))
        cv2.imwrite(boxed_image_path, img)
        print(f"Image with bounding boxes saved to {boxed_image_path}")
        return boxed_image_path
