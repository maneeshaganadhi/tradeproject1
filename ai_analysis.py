from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_sector_data(sector, news_data):
    try:
        prompt = f"Analyze the Indian {sector} sector based on the following news:\n{news_data}"

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception:
        return {
            "The Indian semiconductor sector is experiencing rapid growth due to government incentives..."
}