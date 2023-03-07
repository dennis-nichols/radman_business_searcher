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
from functions import get_place_ids

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
async def root(city: str = None, business_type: str = None):
  
  place_id_list = get_place_ids(city=city, business_type=business_type)
  
  fields_list = ['name', 'formatted_address', 'website', 'formatted_phone_number', 'rating', 'user_ratings_total','url']
  fields = '%2C'.join(fields_list)
  
  results = []
  for place_id in place_id_list:
      details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={key}"
      details_response = requests.get(details_url).json()['result']
      results.append(details_response)

  # create a pandas DataFrame from the results
  details_df = pd.json_normalize(results)

  # convert the DataFrame to a dictionary
  data_dict = details_df.to_dict()

  # extract the values for each column and store them in a new dictionary
  column_values = {}
  for column in data_dict:
      column_values[column] = list(data_dict[column].values())
  for index, address in enumerate(column_values['formatted_address']):
      column_values['formatted_address'][index] = address.replace(",","").replace("#", "No. ")
  
  # send the new dictionary to the front end
   # add the CORS headers to the response
  response = JSONResponse(content=column_values)
  response.headers["Access-Control-Allow-Origin"] = "*"
  response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
  response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, content-type"

  return response
 