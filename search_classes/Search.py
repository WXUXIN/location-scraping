import string
import requests
import urllib.parse
import json
import pandas as pd
import numpy as np
import time
import math
from geographiclib.geodesic import Geodesic
import key_parameters
import geopy
from geopy import distance
from abc import ABC, abstractmethod

nearby_search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'

class Search:
    def __init__(self, google_map_api_key):
        self.google_map_api_key = google_map_api_key

    @abstractmethod
    def load_api_payloads(self, payload_type, **kwargs):
        pass
    
    @abstractmethod
    def main_search(self, df_input):
        pass

    # I want to use single responsiblity principle to break down getting outlets for mall, and getting outlet for busstops
    # Bus stops:
    # loops through 1 point
    # returns [json] list of results for 1 point

    # Shopping area:
    # loops through all search circles in a single area
    # returns [json] list of results for a single area

    def nearby_search(self, dataframe, nearby_search_payload, nearby_search_type):
        search_circle_num = len(dataframe)
        main_results_tracker = []

        # unexpected! If no results then just return empty list
        if search_circle_num == 0:
            return main_results_tracker

        if 'Location' not in dataframe.columns or 'Type' not in dataframe.columns:
            raise ValueError(
                f"Getting circles did not provide required columns (Location & Type)")

        location_name, location_type = dataframe.loc[0,
                                                     'Location'], dataframe.loc[0, 'Type']

        # This is for the entire location
        total_api_call_counter = 0

        # Loops through all the rows of location provided
        for lat, long, call_cap, location, location_type in zip(dataframe['Latitude'], dataframe['Longitude'], dataframe['Call Cap'], dataframe['Location'], dataframe['Type']):
            try:
                api_call_tracker, num_results = 0, 0

                # Load API to get ready for nearby_search for this location
                nearby_search_payload['location'] = f"{lat},{long}"
                nearby_search_payload['type'] = nearby_search_type

                ### API call for 1st page ###
                # A First API call is guaranteed for a particular search circle
                response = requests.get(
                    nearby_search_url, params=nearby_search_payload)
                api_call_tracker += 1
                response = response.json()
                status = response.get('status', " ")
                # Gets initial token, Gets initial results
                token_tracker, results_tracker = response.get(
                    'next_page_token', ''), response.get('results', [])
                if status != "OK":
                    raise ValueError(
                        f"API response status was {status} for nearby_search at the #{api_call_tracker} API call")

                num_results += len(response.get('results', []))
                # Updates payload with initial token
                nearby_search_payload['pagetoken'] = token_tracker
                ##############################

                # While token is valid and we have not reached the call cap, we keep calling
                while token_tracker and (api_call_tracker < int(call_cap)):
                    time.sleep(3)

                    ### API call for subsequent page ###
                    response = requests.get(
                        nearby_search_url, params=nearby_search_payload)
                    api_call_tracker += 1
                    response = response.json()
                    status = response.get('status', " ")
                    token_tracker = response.get('next_page_token', '')
                    if status != "OK":
                        raise ValueError(
                            f"API response status was {status} for nearby_search at the #{api_call_tracker} API call")

                    results_tracker.extend(response.get('results', []))
                    num_results += len(response.get('results', []))
                    nearby_search_payload['pagetoken'] = token_tracker
                    ####################################
            except Exception as e:
                print(
                    f"Error in nearby_search for {location} at {lat}, {long}: \n {e}")
            finally:
                # Adds location and type for each result that it came from
                for result in results_tracker:
                    result['Location'] = location
                    result['Type'] = location_type

                main_results_tracker.extend(results_tracker)
                total_api_call_counter += api_call_tracker
                print(
                    f"# of API calls per circle ({lat}, {long}): {api_call_tracker}, # of results : {len(results_tracker)}")
                continue

        # Store figures in this level to get info on a single Mall / Busstop
        print(f"\nTotal number of API calls per area / point: {total_api_call_counter}\nTotal number of results per area / point: {len(main_results_tracker)}\n")
        # Turn figures into a df and return it
        per_location_stats = pd.DataFrame({'Location': [location_name], "Type": [location_type], "Search Circles": [
            search_circle_num], "Total API calls": [total_api_call_counter], "Number of Outlets": [len(main_results_tracker)]})
        return (main_results_tracker, per_location_stats)