from fastapi import APIRouter
from services.ai_analysis import analyze_sector_data
from utils.markdown_generator import generate_markdown

router = APIRouter()

@router.get("/analyze/{sector}")
def analyze_sector(sector: str):

    ai_result = analyze_sector_data(sector, "sample news data")

    report = generate_markdown(sector, ai_result)

    return {
        "sector": sector,
        "report": report
    }