import numpy as np
import cv2

def segment_lines(pil_image):
    gray = np.array(pil_image.convert("L"))
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    sobel = cv2.Sobel(blurred, cv2.CV_8U, 0, 1, ksize=3)
    _, binary = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (150, 5))
    dilated = cv2.dilate(binary, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    lines = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        lines.append(
            pil_image.crop((0, max(0, y - 5), pil_image.width, y + h + 5))
        )

    return lines
