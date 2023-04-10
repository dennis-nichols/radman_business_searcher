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
import time
import json

load_dotenv()

service_account_info = {
    "type": "service_account",
    "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
    "token_uri": os.environ.get("GOOGLE_TOKEN_URI"),
}
print(len(service_account_info))
creds = service_account.Credentials.from_service_account_info(
    service_account_info)

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

# Place details schema
class PlaceDetail(BaseModel):
    website: str
    user_ratings_total: int
    city: str


# loading in the cities csv file
cities_df = pd.read_csv('cities_1000.csv')

spreadsheet_id = os.getenv("SHEET_ID")

# Function to update or insert a row in the spreadsheet

async def update_or_insert_place(website: str, user_ratings_total: int, city: str, state: str, business_type: str):
    range_name = "Sheet1!A:E"  # Update the range to include columns A to E

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
        range_name = f"Sheet1!B{found_row_index + 1}:E{found_row_index + 1}"
        request = sheets_instance.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": [[user_ratings_total, city, state, business_type]]},
        )
    else:
        # Insert a new row
        request = sheets_instance.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [
                [website, user_ratings_total, city, state, business_type]]},
        )

    response = request.execute()
    print(f"Inserted/Updated website: {website}, result: {response}")


async def update_places(city: str, state: str, business_type: str, place_details: dict):
    counter = 0
    for website, user_ratings_total in zip(place_details['website'], place_details['user_ratings_total']):
        await update_or_insert_place(website, user_ratings_total, city, state, business_type)
        counter += 1
    print(f"Processed {counter} rows.")
    return {"status": "success"}


@app.get("/")
async def root(city: str = None, business_type: str = None, min_ratings: int = 100,
               search_by_state: bool = False, min_population: int = 5000, state: str = None):
    print(
        f"Received parameters: city={city}, business_type={business_type}, min_ratings={min_ratings}, search_by_state={search_by_state}, min_population={min_population}, state={state}")
    if not search_by_state:
        # Get the place ID list based on city, business_type, and minimum ratings
        place_id_list = get_place_ids(
            city=f'{city} {state}', business_type=business_type, min_ratings=min_ratings)
        # Get place details based on the place ID list
        column_values = get_place_details(place_id_list)

        # Send the data to the FastAPI backend
        update_response = await update_places(city,state, business_type, column_values)
        print(update_response)

        response = JSONResponse(content=column_values)
    else:
        if state:
            print('Searching by state')
            # Filter cities by state and minimum population
            filtered_cities = cities_df[(cities_df['state'] == state) & (
                cities_df['population'] >= min_population)]

            for _, row in filtered_cities.iterrows():
                city_name = row['city']
                print(f"Searching for {business_type} in {city_name}, {state}")

                # Get the place ID list based on city, business_type, and minimum ratings
                place_id_list = get_place_ids(
                    city=city_name, business_type=business_type, min_ratings=min_ratings)
                if not place_id_list:
                    print(f"No results found for {city_name}, {state}")
                    continue

                # Get place details based on the place ID list
                column_values = get_place_details(place_id_list)

                # Send the data to the FastAPI backend
                update_response = await update_places(city_name, state, business_type, column_values)
                print(update_response)

                time.sleep(2)  # Wait for 2 seconds between city searches

            response = JSONResponse(content={"message": "Search complete"})
        else:
            response = JSONResponse(
                content={"message": "State parameter is required for search_by_state=True"})

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, content-type"

    return response
