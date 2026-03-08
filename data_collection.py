import requests

def fetch_sector_news(sector):

    url = f"https://newsapi.org/v2/everything?q={sector}&language=en&pageSize=5&apiKey=demo"

    try:
        response = requests.get(url)
        data = response.json()

        articles = []

        for article in data.get("articles", []):
            articles.append({
                "title": article["title"],
                "description": article["description"]
            })

        return articles

    except Exception as e:
        return [{"title": "Error", "description": str(e)}]
