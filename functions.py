import os
import requests
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()
key = os.getenv("PLACES_KEY")


def get_place_ids(city: str = None, business_type: str = None, request_delay: float = 2.0, min_ratings: int = 100):
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
      # print(response_2)
      # Convert response_2 to a dataframe
      df_2 = pd.json_normalize(response_2["results"])
      df_list.append(df_2)  # Append df_2 to df_list

      if response_2.get("next_page_token"):
        token = response_2["next_page_token"]

        # set delay to make sure the API doesn't reject request
        time.sleep(request_delay)
        response_3 = requests.get(next_url).json()
        # print(response_3)
        # Convert response_3 to a dataframe
        df_3 = pd.json_normalize(response_3["results"])
        df_list.append(df_3)  # Append df_3 to df_list

  # Concatenate all dataframes in df_list together
  result_df = pd.concat(df_list, ignore_index=True)
  # filter to only businesses with at least 100 ratings
  filtered_df = result_df.query(f"user_ratings_total > {min_ratings}")

  # get list of place ids to make API calls for more details
  place_id_list = filtered_df['place_id'].tolist()
  
  return place_id_list


def get_place_details(place_id_list):
    """
    Retrieves place details for a list of place IDs using the Google Places API.
    
    Parameters:
        place_id_list (list): A list of place IDs for which details are to be retrieved.
    
    Returns:
        dict: A dictionary containing the values for each column of the retrieved place details.
    """
    # Define the fields to be retrieved
    fields_list = ['website', 'user_ratings_total']
    fields = '%2C'.join(fields_list)

    # Retrieve place details for each place ID
    results = []
    for place_id in place_id_list:
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={key}"
        details_response = requests.get(details_url).json()['result']
        results.append(details_response)

    # Create a pandas DataFrame from the results
    details_df = pd.json_normalize(results)

    # Convert the DataFrame to a dictionary
    data_dict = details_df.to_dict()

    # Extract the values for each column and store them in a new dictionary
    column_values = {}
    for column in data_dict:
        column_values[column] = list(data_dict[column].values())

    # Process the 'website' column and identify duplicate websites
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

    # Remove duplicate entries from the column values
    for column in column_values:
        column_values[column] = [value for i, value in enumerate(
            column_values[column]) if i not in duplicate_indices]
  
    return column_values
