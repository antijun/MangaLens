from PIL import Image, ImageDraw, ImageFont
import textwrap
import csv

def overlay_translated_text(img_path, csv_file_path, output_path, font_path="arial.ttf"):
    """Overlay translated text on the image based on bounding boxes using Pillow."""
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    # Default font size and padding
    default_font_size = 24  # Starting font size
    padding = 10  # Padding between text and bounding box edges

    with open(csv_file_path, "r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header row

        for row in reader:
            original_text, translated_text, x, y, w, h = row
            x, y, w, h = map(int, (x, y, w, h))  # Convert bounding box coordinates to integers

            # Skip placeholder or empty translations
            if translated_text.strip() in ["", "...", "The..."]:
                print(f"Skipping placeholder text: {original_text}")
                continue

            # Skip invalid bounding boxes
            if w <= 0 or h <= 0:
                print(f"Skipping invalid bounding box for text: {translated_text}")
                continue

            # Dynamically calculate font size to fit inside the bounding box
            font_size = default_font_size
            font = ImageFont.truetype(font_path, font_size)

            while True:
                # Wrap text to fit within the bounding box width
                wrapped_text = textwrap.fill(translated_text, width=max(1, (w - 2 * padding) // font_size), break_long_words=False)

                # Calculate total height of the text block
                text_height = len(wrapped_text.split("\n")) * (font_size + 4)

                if text_height <= h - 2 * padding:
                    break  # Text fits within the bounding box
                font_size -= 1
                if font_size < 8:  # Minimum font size threshold
                    print(f"Skipping overlay: Text too large for bounding box: {translated_text}")
                    break
                font = ImageFont.truetype(font_path, font_size)

            # Center text vertically and horizontally within the bounding box
            current_y = y + (h - text_height) // 2

            for line in wrapped_text.split("\n"):
                # Center each line horizontally
                text_width = draw.textlength(line, font=font)
                current_x = x + (w - text_width) // 2

                # Draw shadow for better visibility
                shadow_color = "white"
                text_color = "black"
                shadow_offset = 2

                # Draw shadow
                for offset_x, offset_y in [
                    (-shadow_offset, -shadow_offset),
                    (shadow_offset, -shadow_offset),
                    (-shadow_offset, shadow_offset),
                    (shadow_offset, shadow_offset),
                ]:
                    draw.text((current_x + offset_x, current_y + offset_y), line, font=font, fill=shadow_color)

                # Draw main text
                draw.text((current_x, current_y), line, font=font, fill=text_color)
                current_y += font_size + 4  # Line spacing

    img.save(output_path)
    print(f"Translated image saved to {output_path}")
