import os
import requests
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()
key = os.getenv("PLACES_KEY")


def get_place_ids(city: str = None, business_type: str = None, request_delay: float = 2.0):
  """
  Takes in a city and a business type from the query and returns a list of place IDs from the Google Place Search API.
  """
  
  df_list = []  # Initialize an empty list to store dataframes

  query = f"{business_type} in {city}"

  search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
  response_1 = requests.get(search_url).json()

  df_1 = pd.json_normalize(response_1["results"])
  df_list.append(df_1)  # Append df_2 to df_list

  if response_1.get("next_page_token"):
      token = response_1["next_page_token"]
      next_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={token}&key={key}"
      # set delay to make sure the API doesn't reject request
      time.sleep(request_delay)
      response_2 = requests.get(next_url).json()
      # Convert response_2 to a dataframe
      df_2 = pd.json_normalize(response_2["results"])
      df_list.append(df_2)  # Append df_2 to df_list

      if response_2.get("next_page_token"):
        token = response_2["next_page_token"]

        # set delay to make sure the API doesn't reject request
        time.sleep(request_delay)
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
  
  return place_id_list
