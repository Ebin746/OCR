from .segmentation import segment_lines
from .preprocessing import preprocess_for_trocr
from app.core.trocr_model import processor, model
from app.core.config import DEVICE
from PIL import Image
import torch

def ocr_line(img):
    inputs = processor(images=img, return_tensors="pt").pixel_values.to(DEVICE)
    ids = model.generate(inputs, max_new_tokens=80)
    return processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

def ocr_page(pil_image):
    lines = []
    line_imgs = segment_lines(pil_image)

    for li in line_imgs:
        p = preprocess_for_trocr(li)
        text = ocr_line(p)
        if text:
            lines.append(text)

    return lines
