import os
import json
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

prompt = """
User Query: Give me stats for CSK

Available Functions:
- team_total_matches(team)
- team_total_wins(team)
- team_win_percentage(team)
- team_highest_score(team)

Map short team names (CSK -> Chennai Super Kings, MI -> Mumbai Indians).
Return ONLY a valid JSON list of objects:
[
  {"func": "function_name", "args": {"arg1": "val1"}}
]
"""

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt,
    config=types.GenerateContentConfig(response_mime_type="application/json")
)
print(response.text)
