import pytesseract  # Importing the pytesseract library for OCR (Optical Character Recognition)
import numpy as np  # Importing numpy library for numerical operations
import cv2  # Importing OpenCV library for image processing

def solve_captcha(img):
    # Resize the input image to a fixed size for consistent processing
    img = cv2.resize(img, (1000, 320))

    # Define color ranges for detecting specific colors in the image
    # Range for color red
    lower_red = (0, 0, 100)
    upper_red = (50, 50, 255)

    # Range for color orange
    lower_orange = (0, 80, 150)
    upper_orange = (80, 150, 255)

    # Range for color green
    lower_green = (0, 100, 0)
    upper_green = (50, 255, 50)

    # Create masks for each color range
    mask_red = cv2.inRange(img, lower_red, upper_red)
    mask_orange = cv2.inRange(img, lower_orange, upper_orange)
    mask_green = cv2.inRange(img, lower_green, upper_green)

    # Combine masks for red, orange, and green colors
    final_mask = cv2.bitwise_or(mask_orange, mask_green)
    final_mask = cv2.bitwise_or(final_mask, mask_red)

    # Invert the final mask to get text on a white background
    inverted_mask = cv2.bitwise_not(final_mask)
    white_background = np.full_like(img, (255, 255, 255))  # Create a white background image
    white_background_with_text = cv2.bitwise_or(white_background, white_background, mask=inverted_mask)

    # Apply morphological operations to clean up the image
    kernel = np.ones((3,3), np.uint8)
    result = cv2.morphologyEx(white_background_with_text, cv2.MORPH_OPEN, kernel)

    # Use pytesseract to perform OCR and extract text from the processed image
    text = pytesseract.image_to_string(result, config="--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789")
    text = text.split("\n")[0]  # Extract the first line of the detected text

    return text  # Return the extracted text
