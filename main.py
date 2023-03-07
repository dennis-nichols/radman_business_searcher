from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import time
import json
import io

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
  
  df_list = []  # Initialize an empty list to store dataframes
  
  query = f"{business_type} in {city}"
  search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
  response_1 = requests.get(search_url).json()


  df_1 = pd.json_normalize(response_1["results"])
  df_list.append(df_1)  # Append df_2 to df_list
  

  if response_1.get("next_page_token"):
    token = response_1["next_page_token"]
    next_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={token}&key={key}"
    time.sleep(2)
    response_2 = requests.get(next_url).json()
    # Convert response_2 to a dataframe
    df_2 = pd.json_normalize(response_2["results"])
    df_list.append(df_2)  # Append df_2 to df_list
    
    if response_2.get("next_page_token"):
      token = response_2["next_page_token"]
      next_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={token}&key={key}"
      time.sleep(2)
      response_3 = requests.get(next_url).json()
      # Convert response_3 to a dataframe
      df_3 = pd.json_normalize(response_3["results"])
      df_list.append(df_3)  # Append df_3 to df_list

  # Concatenate all dataframes in df_list together
  result_df = pd.concat(df_list, ignore_index=True)
  # filter to only businesses with at least 100 ratings
  filtered_df = result_df.query("user_ratings_total > 100")
  
  # get list of place ids to make API calls for more details
  place_id_list = filtered_df['place_id'].tolist()
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

  # send the new dictionary to the front end
  return column_values
 