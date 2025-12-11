````markdown
# 📝 OCR Extraction & Field Verification API  
A production-ready OCR backend built using **FastAPI**, **HuggingFace TrOCR**, and clean modular architecture.

---

## 🚀 Features
- Extract text from **images & PDFs**
- Line segmentation for improved OCR
- High-accuracy **TrOCR** text extraction
- Automatic field detection & normalization
- Field comparison with confidence scoring
- Organized clean architecture (FastAPI best practices)
- Static frontend support (index.html)

---

## 📁 Project Structure

```plaintext
app/
├── main.py
├── api/
│   ├── routes_extract.py
│   └── routes_compare.py
├── core/
│   ├── config.py
│   └── trocr_model.py
├── ocr/
│   ├── segmentation.py
│   ├── preprocessing.py
│   └── extractor.py
├── utils/
│   ├── fields.py
│   ├── validation.py
│   └── similarity.py
└── static/
    └── index.html
````

---

## 🛠 Installation

```bash
git clone <repo-url>
cd OCR
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## ▶️ Run the Server

```bash
uvicorn app.main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

Frontend:

```
http://127.0.0.1:8000/
```

---

## 📤 API Documentation

### POST /extract

Extracts structured fields from an uploaded image/PDF.

**Request**

```
file: <image or pdf>
```

**Response Example**

```json
{
  "fields": {
    "first_name": "John",
    "date_of_birth": "12/03/1998",
    "postal_code": "682301"
  }
}
```

---

### POST /compare

Compares extracted vs submitted fields and returns confidence score.

**Request**

```json
{
  "extracted": { "first_name": "John" },
  "submitted": { "first_name": "Jhon" }
}
```

**Response**

```json
{
  "overall_confidence": 87.5,
  "fields": {
    "first_name": {
      "extracted": "John",
      "submitted": "Jhon",
      "confidence": 87.5
    }
  }
}
```

---

## 🔍 How It Works (Data Flow)

1. User uploads an image/PDF
2. OCR engine segments text lines
3. Image enhancement (CLAHE, denoise)
4. TrOCR performs text extraction
5. Field extractor maps labels → values
6. Validator cleans & normalizes values
7. Output returned as structured JSON
8. `/compare` optionally verifies user-entered data

---

## 📦 Why `app.` is required in imports?

Because `app/` is the root package.
Python requires full paths like:

```python
from app.ocr.extractor import ocr_page
```

This ensures reliable imports when running FastAPI or Uvicorn.

---

## 🗂 Why every folder needs `__init__.py`?

`__init__.py` turns folders into Python packages.
Without it, Python **cannot import** modules inside them.

---

## 🔮 Future Enhancements

* Multi-page PDF OCR
* Hindi / Arabic OCR expansion
* NER-based field extraction
* Per-line confidence scoring
* Docker deployment support

---


