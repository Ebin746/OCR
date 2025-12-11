from fastapi import APIRouter, UploadFile, File
from app.ocr.extractor import ocr_page
from app.utils.fields import extract_fields
from app.utils.validation import validate
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO

router = APIRouter()

@router.post("/")
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
