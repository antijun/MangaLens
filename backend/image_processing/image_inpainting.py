import os
import sys
import tensorflow as tf
import numpy as np

# Add SickZil-Machine to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../SickZil-Machine/src"))

import core
import imgio

class ImageInpainter:
    def __init__(self):
        pass

    def inpaint(self, originalImage, maskImage):
        """Generate the inpainted image."""
        return core.inpainted(originalImage, maskImage)

    def save_image(self, outputPath, fileName, image):
        """Save the image to the specified path."""
        os.makedirs(outputPath, exist_ok=True)
        imgio.save(os.path.join(outputPath, fileName), image)