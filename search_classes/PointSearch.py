import string
import requests
import urllib.parse
from search_classes.Search import Search
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


class PointSearch(Search):
    def __init__(self, google_map_api_key, df_input):
        super().__init__(google_map_api_key)
        self.df_input = df_input
        self.point_nearby_search_payload = None
        self.fill_missing_values()

    def fill_missing_values(self):
        # using fillna() to fill missing values
        # self.df_input['Call Cap'] = self.df_input['Call Cap'].fillna(key_parameters.POINT_CIRCLE_NEARBY_SEARCH_CALL_CAP)
        self.df_input.loc[self.df_input['Call Cap'].isna(), 'Call Cap'] = key_parameters.POINT_CIRCLE_NEARBY_SEARCH_CALL_CAP

    def load_api_payloads(self, payload_type, **kwargs):
        if (payload_type == 'point_nearby_search'):
            if 'radius' not in kwargs:
                raise ValueError("No radius")
            else:
                kwargs['key'] = self.google_map_api_key
                self.point_nearby_search_payload = kwargs
    
    def main_search(self):
        if self.df_input is None:
            raise ValueError("No points provided")

        all_point_results_tracker = []
        all_point_stats_tracker = []
        for lat, long, call_cap, location, location_type in zip(self.df_input['Latitude'], self.df_input['Longitude'], self.df_input['Call Cap'], self.df_input['Location'], self.df_input['Type']):
            # Between calls we must wait as well
            time.sleep(3)
            nearby_search_input_df = pd.DataFrame({'Latitude': [lat], 'Longitude': [
                long], 'Location': [location]                
                , 'Call Cap': [call_cap], "Type": [location_type]})
            print(f"############ Searching for {location}.... ############ ")
            single_point_circles_search, single_point_stats = self.nearby_search(
                nearby_search_input_df, self.point_nearby_search_payload, key_parameters.NEARBY_SEARCH_TYPE)
            all_point_results_tracker.extend(single_point_circles_search)
            all_point_stats_tracker.append(single_point_stats)

        # This is to get all the data
        point_places_df = pd.json_normalize(all_point_results_tracker)
        source_places__point_df = point_places_df.drop_duplicates(
            subset=['place_id'], keep='first').sort_values('place_id')
        source_stats__point_df = pd.concat(all_point_stats_tracker)
        return (source_places__point_df, source_stats__point_df)
