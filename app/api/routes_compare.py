from fastapi import APIRouter
from app.utils.similarity import similarity

router = APIRouter()

@router.post("/")
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
