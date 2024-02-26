import pytesseract
import numpy as np
import cv2

def solve_captcha(img):

    # img = cv2.imread(image_filename)
    img = cv2.resize(img, (1000, 320))
    # img = cv2.resize(img, (1100, 350))

    # Range for color red
    lower_red = (0, 0, 100)
    upper_red = (50, 50, 255)

    # Range for color orange
    lower_orange = (0, 80, 150)
    upper_orange = (80, 150, 255)

    # Range for color green
    lower_green = (0, 100, 0)
    upper_green = (50, 255, 50)

    mask_red = cv2.inRange(img, lower_red, upper_red)
    mask_orange = cv2.inRange(img, lower_orange, upper_orange)
    mask_green = cv2.inRange(img, lower_green, upper_green)

    final_mask = cv2.bitwise_or(mask_orange, mask_green)
    final_mask = cv2.bitwise_or(final_mask, mask_red)

    inverted_mask = cv2.bitwise_not(final_mask)
    white_background = np.full_like(img, (255, 255, 255))
    white_background_with_text = cv2.bitwise_or(white_background, white_background, mask=inverted_mask)

    kernel = np.ones((3,3), np.uint8)
    result = cv2.morphologyEx(white_background_with_text, cv2.MORPH_OPEN, kernel)

    text = pytesseract.image_to_string(result, config="--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789")
    text = text.split("\n")[0]

    # cv2.imshow("image", result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return text

