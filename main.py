from fastapi import FastAPI
import os
import requests
from dotenv import load_dotenv
import pandas

load_dotenv()
key = os.getenv("PLACES_KEY")

app = FastAPI()

@app.get("/")
async def root(city: str = None, business_type: str = None):
  
  query = f"{business_type} in {city}"
  search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
  response_1 = requests.get(search_url).json()
  
  if response_1.get("next_page_token"):
    print("True")
  
  return response_1