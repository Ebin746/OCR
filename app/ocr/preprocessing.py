import cv2
import numpy as np
from PIL import Image

def preprocess_for_trocr(img):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    denoise = cv2.fastNlMeansDenoising(gray, h=25)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoise)

    return Image.fromarray(enhanced).convert("RGB")
