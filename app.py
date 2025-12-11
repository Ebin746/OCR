import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import torch
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import re
from datetime import datetime
from difflib import SequenceMatcher

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from pdf2image import convert_from_bytes


# ================================================================
# FASTAPI BASICS
# ================================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")


# ================================================================
# LOAD TrOCR MODEL
# ================================================================

MODEL = "microsoft/trocr-small-handwritten"
processor = TrOCRProcessor.from_pretrained(MODEL)
model = VisionEncoderDecoderModel.from_pretrained(MODEL)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


# ================================================================
# OCR UTILITIES
# ================================================================

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
        cropped = pil_image.crop((0, max(0, y-5), pil_image.width, y+h+5))
        lines.append(cropped)

    return lines


def preprocess_for_trocr(img):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    denoise = cv2.fastNlMeansDenoising(gray, h=25)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoise)
    return Image.fromarray(enhanced).convert("RGB")


def ocr_line(img):
    inputs = processor(images=img, return_tensors="pt").pixel_values.to(device)
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


# ================================================================
# FIELD EXTRACTION
# ================================================================

def split_label_value(text):
    for sep in [":", "-", "=", "–"]:
        if sep in text:
            left, right = text.split(sep, 1)
            return left.strip(), right.strip()
    return None, text.strip()


def map_label(l):
    if not l: return None
    s = l.lower()

    if "first" in s: return "first_name"
    if "middle" in s: return "middle_name"
    if "last" in s: return "last_name"
    if "gender" in s: return "gender"
    if "birth" in s or "dob" in s: return "date_of_birth"
    if "address" in s and "1" in s: return "address_line_1"
    if "address" in s and "2" in s: return "address_line_2"
    if "city" in s: return "city"
    if "state" in s: return "state"
    if "pin" in s: return "postal_code"
    if "phone" in s or "mobile" in s: return "phone_number"
    if "email" in s: return "email"

    return None

def extract_fields(lines):
    fields = {}

    for line in lines:
        label, value = split_label_value(line)

        if not value:
            continue

        key = map_label(label)

        if key is None:
            if label is None or label.strip() == "":
                auto = f"field_{len(fields)+1}"
            else:
                auto = label.lower().replace(" ", "_")

            fields[auto] = value
        else:
            fields[key] = value

    return fields


# ================================================================
# VALIDATION
# ================================================================

def validate(fields):
    verified = {}

    for k, v in fields.items():
        original = v
        val = v.strip()

        if "name" in k:
            new = re.sub(r"[^A-Za-z ]", "", val)
            verified[k] = new
        elif "gender" in k:
            if "male" in val.lower(): verified[k] = "Male"
            elif "female" in val.lower(): verified[k] = "Female"
            else: verified[k] = val
        elif "birth" in k:
            verified[k] = val
        elif "phone" in k:
            digits = re.sub(r"\D", "", val)
            verified[k] = digits[-10:]
        elif "pin" in k:
            digits = re.sub(r"\D", "", val)
            verified[k] = digits[:6]
        else:
            verified[k] = val

    return verified


# ================================================================
# CONFIDENCE SCORE API
# ================================================================

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

@app.post("/compare")
async def compare_api(data: dict):
    extracted = data.get("extracted", {})
    submitted = data.get("submitted", {})

    report = {}
    total = 0
    count = 0

    for key in submitted:
        ext = extracted.get(key, "")
        sub = submitted[key]

        score = similarity(ext, sub)
        total += score
        count += 1

        report[key] = {
            "extracted": ext,
            "submitted": sub,
            "confidence": round(score * 100, 2)
        }

    final_score = round((total / count) * 100, 2)

    return {
        "overall_confidence": final_score,
        "fields": report
    }


# ================================================================
# OCR ENDPOINT
# ================================================================

@app.post("/extract")
async def extract_api(file: UploadFile = File(...)):
    content = await file.read()

    if file.filename.endswith(".pdf"):
        pages = convert_from_bytes(content)
        lines = ocr_page(pages[0])
    else:
        img = Image.open(BytesIO(content)).convert("RGB")
        lines = ocr_page(img)

    fields = extract_fields(lines)
    verified = validate(fields)

    return {"fields": verified}


# ================================================================
# RUN SERVER
# ================================================================

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
