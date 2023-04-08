from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import time
import json
import io
from functions import get_place_ids, get_place_details

load_dotenv()
key = os.getenv("PLACES_KEY")


app = FastAPI()

# Allow all origins to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(city: str = None, business_type: str = None, min_ratings: int = 100):
  
  place_id_list = get_place_ids(city=city, business_type=business_type, min_ratings=min_ratings)
  column_values = get_place_details(place_id_list)
  
 
  response = JSONResponse(content=column_values)
  response.headers["Access-Control-Allow-Origin"] = "*"
  response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
  response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, content-type"

  return response
 