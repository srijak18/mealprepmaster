import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def generate_recipes_with_gemini(ingredients):
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY in environment variables")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"Suggest 3 healthy and easy recipes using these ingredients: {ingredients}. Each recipe should include a title, short description, ingredients list, and instructions."
            }]
        }]
    }

    response = requests.post(f"{url}?key={GOOGLE_API_KEY}", json=data, headers=headers)
    response.raise_for_status()
    return response.json()['candidates'][0]['content']['parts'][0]['text']
