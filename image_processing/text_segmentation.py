import os
import sys
import cv2
from .image_inpainting import ImageInpainter


# Add SickZil-Machine to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../SickZil-Machine/src"))

import core
import imgio
import utils.fp as fp

class TextSegmentation:
    def __init__(self):
        self.inpainter = ImageInpainter()

    def imgpath2mask(self, imgpath):
        """Generate a mask from the image path using SickZil-Machine."""
        return fp.go(
            imgpath,
            lambda path: imgio.load(path, imgio.NDARR),
            core.segmap,
            imgio.segmap2mask,
        )

    def resize(self, imgPath):
        """
        Resize the image to have a height of 1000px to ensure compatibility 
        with SickZil-Machine, which struggles with high-resolution images.
        """
        img = cv2.imread(imgPath)
        size = 1000
        if img.shape[0] > size:
            img = cv2.resize(img, (int(size * img.shape[1] / img.shape[0]), size), interpolation=cv2.INTER_AREA)
            cv2.imwrite(imgPath, img)

    def segmentPage(self, imgPath, outputInpaintedPath, outputTextOnlyPath):
        """
        Process the image to generate inpainted and text-only outputs.
        """
        # Resize the image
        self.resize(imgPath)

        # Process with SickZil-Machine
        fileName = os.path.basename(imgPath)
        originalImage = imgio.load(imgPath, imgio.IMAGE)  # Original image
        maskImage = imgio.mask2segmap(self.imgpath2mask(imgPath))  # Mask image

        # Generate inpainted output
        inpaintedImage = self.inpainter.inpaint(originalImage, maskImage)

        # Generate text-only output
        textOnlyImage = cv2.bitwise_and(originalImage, maskImage)  # Text-only image
        textOnlyImage[maskImage == 0] = 255  # Set background to white

        # Save results
        self.inpainter.save_image(outputInpaintedPath, fileName, inpaintedImage)
        self.inpainter.save_image(outputTextOnlyPath, fileName, textOnlyImage)

        print(f"Inpainted image saved to {os.path.join(outputInpaintedPath, fileName)}")
        print(f"Text-only image saved to {os.path.join(outputTextOnlyPath, fileName)}")
        return (
            os.path.join(outputInpaintedPath, fileName),
            os.path.join(outputTextOnlyPath, fileName),
        )

# Example usage
if __name__ == "__main__":
    image_path = "test_panels/mushoku2.jpg"
    output_inpainted_dir = "output/inpainted/"
    output_text_only_dir = "output/text_only/"

    segmenter = TextSegmentation()
    inpainted_path, text_only_path = segmenter.segmentPage(image_path, output_inpainted_dir, output_text_only_dir)
    print(f"Segmentation completed. Results:\nInpainted: {inpainted_path}\nText-only: {text_only_path}")