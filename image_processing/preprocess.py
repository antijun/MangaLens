import os
import cv2

def resize_image(image, max_height=1000):
    if image.shape[0] > max_height:
        scale_factor = max_height / image.shape[0]
        new_width = int(image.shape[1] * scale_factor)
        image = cv2.resize(image, (new_width, max_height), interpolation=cv2.INTER_AREA)
    return image

def enhance_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

def preprocess_image(image_path):
    # load image
    image = cv2.imread(image_path)
    
    # resize image
    image = resize_image(image)

    # convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    contrasted_image = enhance_contrast(gray_image)
    
    return contrasted_image

# processed_image = preprocess_image("test_panels/mushoku2.jpg")
# cv2.imshow("Processed Image", processed_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()