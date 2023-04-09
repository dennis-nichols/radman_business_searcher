import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from functions import get_place_ids, get_place_details

load_dotenv()

# Load the Service Account credentials
creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
)

sheets_instance = build("sheets", "v4", credentials=creds)
spreadsheet_name = "Business Searcher Database"  # Replace with your spreadsheet name

app = FastAPI()

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


spreadsheet_id = os.getenv("SHEET_ID")

# Updated function to include city and business_type columns


async def update_or_insert_place(website: str, user_ratings_total: int, city: str, business_type: str):
    range_name = "Sheet1!A:D"  # Update the range to include columns A to D

    request = sheets_instance.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name
    )
    response = request.execute()

    rows = response.get("values", [])

    found_row = None
    for row in rows:
        if row[0] == website:
            found_row = row
            break

    if found_row:
        # Update the row
        found_row_index = rows.index(found_row)
        range_name = f"Sheet1!B{found_row_index + 1}:D{found_row_index + 1}"
        request = sheets_instance.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": [[user_ratings_total, city, business_type]]},
        )
    else:
        # Insert a new row
        request = sheets_instance.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [
                [website, user_ratings_total, city, business_type]]},
        )

    response = request.execute()
    print(f"Inserted/Updated website: {website}, result: {response}")


async def update_places(city: str, business_type: str, place_details: dict):
    counter = 0
    for website, user_ratings_total in zip(place_details['website'], place_details['user_ratings_total']):
        await update_or_insert_place(website, user_ratings_total, city, business_type)
        counter += 1
    print(f"Processed {counter} rows.")
    return {"status": "success"}


@app.get("/")
async def root(city: str = None, business_type: str = None, min_ratings: int = 100):
    # Get the place ID list based on city, business type, and minimum ratings
    place_id_list = get_place_ids(
        city=city, business_type=business_type, min_ratings=min_ratings)
    # Get place details based on the place ID list
    column_values = get_place_details(place_id_list)

    # Send the data to the FastAPI backend
    update_response = await update_places(city, business_type, column_values)
    print(update_response)

    response = JSONResponse(content=column_values)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, content-type"

    return response
