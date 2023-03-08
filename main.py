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
async def root(city: str = None, business_type: str = None, min_ratings: int = 100):
  
  place_id_list = get_place_ids(city=city, business_type=business_type, min_ratings=min_ratings)
  
  fields_list = ['website', 'user_ratings_total']
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
  print(column_values['website'])
  duplicate_indices = set()
  seen = set()
  for index, site in enumerate(column_values['website']):
      if type(site) != str:
        column_values['website'][index] = 'No website'
      else:
        site = site.split("//")[-1].split("/")[0]
        if "www." not in site:
            site = "www." + site
        if site in seen:
            duplicate_indices.add(index)
        else:
            seen.add(site)
        column_values['website'][index] = site 
      
  for column in column_values:
      column_values[column] = [value for i, value in enumerate(
          column_values[column]) if i not in duplicate_indices]
  print(column_values)
  # send the new dictionary to the front end
   # add the CORS headers to the response
  response = JSONResponse(content=column_values)
  response.headers["Access-Control-Allow-Origin"] = "*"
  response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
  response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, content-type"

  return response
 