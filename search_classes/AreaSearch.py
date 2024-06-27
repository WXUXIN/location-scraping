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

text_search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'


class AreaSearch(Search):
    # we would need all the APIs for text search, nearby search
    def __init__(self, google_map_api_key, df_input):
        super().__init__(google_map_api_key)
        self.df_input = df_input
        self.area_search_radius_buffer = key_parameters.AREA_SEARCH_RADIUS_BUFFER
        self.area_circle_nearby_search_payload = None
        self.text_search_payload = None

    def load_api_payloads(self, payload_type, **kwargs):
        if (payload_type == 'text_search'):
            if len(kwargs.get('location', '').split(',')) < 2:
                raise ValueError("Invalid location")
            elif 'radius' not in kwargs:
                raise ValueError("No radius")
            else:
                kwargs['key'] = self.google_map_api_key
                self.text_search_payload = kwargs
        elif (payload_type == 'area_circle_nearby_search'):
            if 'radius' not in kwargs:
                raise ValueError("No radius")
            elif kwargs.get('radius', 0) <= self.area_search_radius_buffer:
                raise ValueError(
                    f"Radius too small, need to be greater than {self.area_search_radius_buffer}m")
            else:
                kwargs['key'] = self.google_map_api_key
                self.area_circle_nearby_search_payload = kwargs

    # @title Text search to get information on 1 area
    def text_search(self, dataframe):
        self.text_search_payload['query'] = dataframe.loc[0, 'Location']
        response = requests.get(text_search_url, self.text_search_payload)
        response = response.json()
        status = response.get('status', " ")

        # We need to also make sure the place is actually in Singapore
        if 'results' in response and status == 'OK':
            # Specify the path to the 'results' list in the JSON data
            data_path = ['results'][0]

            # Extract data using json_normalize
            df = pd.json_normalize(response, record_path=data_path)

            # If 'geometry.location.lat': 'lat', 'geometry.location.lng' don't exist, raise error
            if 'geometry.location.lat' not in df.columns or 'geometry.location.lng' not in df.columns:
                raise ValueError(
                    "Latitude and Longitude not found in the API response")
            location_coordinate = (float(df.loc[0, 'geometry.location.lat']), float(
                df.loc[0, 'geometry.location.lng']))

            lat_str, lng_str = self.text_search_payload.get(
                'location', '').split(',')
            country_of_interest_coordinates = (
                float(lat_str.strip()), float(lng_str.strip()))
            distance_diff = distance.distance(
                location_coordinate, country_of_interest_coordinates).m

            # Just in case if text search returns a location that is outside the confined search region
            if distance_diff > self.text_search_payload.get('radius', 0):
                raise ValueError(
                    f"Location is outside of {self.text_search_payload.get('region', 'country of interest')}")

            # Display the resulting DataFrame
            final_df = df
            final_df['Location'] = dataframe.loc[0, 'Location']
            final_df['Type'] = dataframe.loc[0, 'Type']
            return final_df
        else:
            raise ValueError(
                f"API response did not return expected results or status was {status} for text search")

    # Getting circles in 1 area
    def getting_circles(self, final_df, circle_radius):
        # these 2 coordinates will form a rectangle
        # Suntec Data
        # northEast = (1.2978256, 103.859935)
        # southWest = (1.2934572, 103.8568782)

        # Renaming columns that are from text search
        column_mapping = {
            'geometry.location.lat': 'lat',
            'geometry.location.lng': 'long',
            'geometry.viewport.northeast.lat': 'northeast_lat',
            'geometry.viewport.northeast.lng': 'northeast_long',
            'geometry.viewport.southwest.lat': 'southwest_lat',
            'geometry.viewport.southwest.lng': 'southwest_long'
        }

        for name in column_mapping.keys():
            if name not in final_df.columns:
                raise ValueError(
                    f"Text search did not return the required columns")

        # List of columns to extract from 'final_df'
        columns_to_extract = list(column_mapping.keys())

        selected_df = final_df[columns_to_extract].rename(
            columns=column_mapping)
        first_row = selected_df.iloc[0]
        northEast = (float(first_row['northeast_lat']),
                     float(first_row['northeast_long']))
        southWest = (float(first_row['southwest_lat']),
                     float(first_row['southwest_long']))

        southEast, northWest = (
            southWest[0], northEast[1]), (northEast[0], southWest[1])
        # calculate bearing from southWest to northWest, # calculate bearing from southEast to northEast
        # https://techoverflow.net/2022/11/02/how-to-compute-distance-and-bearing-between-two-lat-lon-points-in-python/
        bearing_sw_nw = Geodesic.WGS84.Inverse(*southWest, *northWest)["azi1"]
        bearing_se_ne = Geodesic.WGS84.Inverse(*southEast, *northEast)["azi1"]
        bearing_sw_se = Geodesic.WGS84.Inverse(*southWest, *southEast)["azi1"]

        search_circle_area = math.pi * \
            (circle_radius - self.area_search_radius_buffer) ** 2
        # the area of the rectangle
        # find the distance of difference between the latitudes
        distance_lat = distance.distance(northEast, southEast).m
        # find the distance of difference between the longitudes
        distance_long = distance.distance(northEast, northWest).m
        rectangular_area = distance_lat * distance_long
        number_of_circles = math.ceil(
            rectangular_area / search_circle_area)
        print(f"# of circles: {number_of_circles}\n")
        left_num_circles = number_of_circles // 2
        right_num_circles = number_of_circles - left_num_circles
        # split the rectangle into 2, with number_of_circles/2 circles in each rectangle
        # find the coordinates of the circles in the rectangles
        centre_of_circles = []

        new_long_left = geopy.distance.distance(
            meters=distance_long / 4).destination(southWest, bearing=bearing_sw_se)
        new_long_right = geopy.distance.distance(
            meters=distance_long / 4).destination(southEast, bearing=-1 * bearing_sw_se)

        for i in range(left_num_circles):
            # latitude of the circle
            # bearing here cannot assume to be 90, as the bearing is the angle from the north direction

            lat = geopy.distance.distance(meters=(
                i + 0.5) * (distance_lat / left_num_circles)).destination(southWest, bearing=bearing_sw_nw)
            centre_of_circles.append(
                ('left', lat.latitude, new_long_left.longitude))

        for j in range(right_num_circles):
            # latitude of the circle
            lat = geopy.distance.distance(meters=(
                j + 0.5) * (distance_lat / right_num_circles)).destination(southEast, bearing=bearing_se_ne)
            centre_of_circles.append(
                ('right', lat.latitude, new_long_right.longitude))

        # I want to convert centre_of_circles to a dataframe, so that I can use it to loop through the circles in the next step
        # with Call Cap at 3 per circle, so each row would have call_cap = 3

        centre_of_circles_df = pd.DataFrame(centre_of_circles, columns=[
                                            'side', 'Latitude', 'Longitude'])
        centre_of_circles_df['Call Cap'] = key_parameters.AREA_CIRCLE_NEARBY_SEARCH_CALL_CAP
        centre_of_circles_df['Location'] = final_df.loc[0, 'Location']
        centre_of_circles_df['Type'] = final_df.loc[0, 'Type']
        return centre_of_circles_df

    def main_search(self):
        if self.df_input is None:
            raise ValueError("No area data provided")
        all_area_results_tracker = []
        all_area_stats_tracker = []
        all_area_search_circles = []
        for lat, long, call_cap, location, location_type in zip(self.df_input['Latitude'], self.df_input['Longitude'], self.df_input['Call Cap'], self.df_input['Location'], self.df_input['Type']):
            text_search_input_df = pd.DataFrame({'Latitude': [lat], 'Longitude': [
                                                long], 'Location': [location], "Type": [location_type]})
            try:
                print(
                    f"############ Starting Search for {location}.... ############\n")
                single_area_info = self.text_search(text_search_input_df)
                # This is where the call cap for each search circle is placed
                single_area_search_circles = self.getting_circles(
                    single_area_info, self.area_circle_nearby_search_payload['radius'])
            except Exception as e:
                print(f"Error {e} occured for {location} ({lat}, {long})")
                # Need to add in info of areas that met with exception
                single_area_stats = pd.DataFrame({'Location': [location], "Type": [
                    location_type], "Search Circles": 'NIL', "Total API calls": 'NIL', "Number of Outlets": e})
            else:
                print(f"Searching for {location}....")
                single_area_circles_search_result, single_area_stats = self.nearby_search(
                    single_area_search_circles, self.area_circle_nearby_search_payload, key_parameters.NEARBY_SEARCH_TYPE)
                all_area_results_tracker.extend(
                    single_area_circles_search_result)
                all_area_search_circles.append(single_area_search_circles)
            finally:
                all_area_stats_tracker.append(single_area_stats)

        # This is to get all the data
        area_places_df = pd.json_normalize(all_area_results_tracker)
        source_places__area_df = area_places_df.drop_duplicates(
            subset=['place_id'], keep='first').sort_values('place_id')
        source_stats__area_df = pd.concat(all_area_stats_tracker)
        source_search_circles_area = pd.concat(all_area_search_circles)
        return (source_places__area_df, source_stats__area_df, source_search_circles_area)
