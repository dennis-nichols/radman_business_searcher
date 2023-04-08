from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from databases import Database, DatabaseURL
import os
import asyncio
from dotenv import load_dotenv
import pandas as pd
from functions import get_place_ids, get_place_details

load_dotenv()
key = os.getenv("PLACES_KEY")
db_url = os.getenv("DB_URL")

app = FastAPI()
database = Database(
    DatabaseURL(db_url),
    min_size=1,
    max_size=3,  # Adjust this value based on the number of concurrent connections needed
)


# connect and disconnect to the database on startup and shutdown
@app.on_event("startup")
async def startup():
    await database.connect()
    print("Connected to database")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Allow all origins to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlaceDetail(BaseModel):
    website: str
    user_ratings_total: int
    city: str


async def update_or_insert_place(website: str, user_ratings_total: int, city: str):
    query = f"""
    INSERT INTO places (website, user_ratings_total, city)
    VALUES (:website, :user_ratings_total, :city)
    ON CONFLICT (website) DO UPDATE
    SET user_ratings_total = EXCLUDED.user_ratings_total,
        city = EXCLUDED.city;
    """

    values = {"website": website,
              "user_ratings_total": user_ratings_total, "city": city}
    result = await database.execute(query, values)
    print(f"Inserted/Updated website: {website}, result: {result}")


async def update_places(city: str, place_details: dict):
  counter = 0
  for website, user_ratings_total in zip(place_details['website'], place_details['user_ratings_total']):
      await update_or_insert_place(website, user_ratings_total, city)
      counter += 1
  print(f"Processed {counter} rows.")
  return {"status": "success"}


@app.get("/")
async def root(city: str = None, business_type: str = None, min_ratings: int = 100):
  
  place_id_list = get_place_ids(city=city, business_type=business_type, min_ratings=min_ratings)
  column_values = get_place_details(place_id_list)
  
  # Send the data to the FastAPI backend
  update_response = await update_places(city, column_values)
  print(update_response)
 
  response = JSONResponse(content=column_values)
  response.headers["Access-Control-Allow-Origin"] = "*"
  response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
  response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, content-type"

  return response
 