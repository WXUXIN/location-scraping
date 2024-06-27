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
import os
from datetime import datetime

# URL for onemap API
one_map_search_url = "https://www.onemap.gov.sg/api/common/elastic/search?"
reverse_geocode_url = "https://www.onemap.gov.sg/api/public/revgeocode?"
one_map_getToken_url = "https://www.onemap.gov.sg/api/auth/post/getToken"
google_maps_reverse_geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?"
google_maps_place_details_url = "https://maps.googleapis.com/maps/api/place/details/json?"
output_folder_path = key_parameters.OUTPUT_FOLDER_PATH
os.makedirs(output_folder_path, exist_ok=True)
# csv_time = datetime.now().isoformat(sep=" ")

class Crobat():
    def __init__(self, google_map_api_key, onemap_email, onemap_password):
        # API key
        self.onemap_email = onemap_email
        self.onemap_password = onemap_password
        self.google_map_api_key = google_map_api_key
        self.one_map_api_access_token = self.get_onemap_token()
        # user to determine who using what
        self.reverse_geocode_payload = None
        self.reverse_geocode_header = None
        self.google_maps_reverse_geocode_payload = None
        self.google_maps_place_details_payload = None

    def load_api_payloads(self, payload_type, **kwargs):
        # Depending on the api type, i want to load for the different APIs, create a function that takes in multiple api types and keyword arguments
        if (payload_type == 'reverse_geocode'):
            if 'buffer' not in kwargs:
                raise ValueError("No buffer")
            elif 'addressType' not in kwargs:
                raise ValueError("No addressType")
            elif 'otherFeatures' not in kwargs:
                raise ValueError("No otherFeatures")
            else:
                self.reverse_geocode_payload = kwargs
        elif (payload_type == 'reverse_geocode_header'):
            self.reverse_geocode_header = {
                "Authorization": f"Bearer {self.one_map_api_access_token}"}
        elif (payload_type == 'google_maps_reverse_geocode'):
            kwargs['key'] = self.google_map_api_key
            self.google_maps_reverse_geocode_payload = kwargs
        elif (payload_type == 'google_maps_place_details'):
            kwargs['key'] = self.google_map_api_key
            self.google_maps_place_details_payload = kwargs

    def get_onemap_token(self):
        # Get token for onemap API
        onemap_payload = {
            'email': self.onemap_email,
            'password': self.onemap_password
        }
        response = requests.post(one_map_getToken_url, json=onemap_payload, headers={
                                 "Content-Type": "application/json"})
        response = response.json()
        if ('access_token' not in response) or (not response.get("access_token", "")):
            raise ValueError(
                "Latitude and Longitude not found in the API response")
        # This access token will expire after 3 days
        one_map_api_access_token = response.get("access_token", "")
        return one_map_api_access_token

    def reverse_geocode(self, lat, long):
        self.reverse_geocode_payload['location'] = f"{lat},{long}"
        try:
            # If this is takeing more than 10 seconds, we need to return None
            response = requests.get(
                reverse_geocode_url, params=self.reverse_geocode_payload, headers=self.reverse_geocode_header, timeout=10)
            response = response.json()

            # Correcting the data path to access the first element in 'GeocodeInfo'
            data_path = response.get('GeocodeInfo', [])

            # Only if there are results returned
            if len(data_path) > 0:
                # Then we get the 1st result
                df = pd.json_normalize(data_path)
                return df['POSTALCODE'].astype(str).iloc[0] if 'POSTALCODE' in df.columns else None
            else:
                return None
        except requests.exceptions.Timeout:
            print("Timeout error during reverse geocoding")
            return None
        except Exception as e:
            print(f"Error during reverse geocoding: {e}")
            return None

    def reverse_geocode_google(self, lat, long):
        ### Google portion ###
        self.google_maps_reverse_geocode_payload['latlng'] = f'{lat}, {long}'
        google_response = requests.get(
            google_maps_reverse_geocode_url, params=self.google_maps_reverse_geocode_payload)
        google_response = google_response.json()

        ### Google Map portion ###
        # Extract the results from the response
        google_data_path = google_response.get('results', [])

        # Check if there are any results
        if google_data_path:
            first_result = google_data_path[0]
            address_components = first_result.get('address_components', [])
            if address_components:
                postal_code_list = [
                    component for component in address_components if 'postal_code' in component.get('types', [])]
                if postal_code_list:
                    # Add the postal code to the row
                    # print(postal_code_list[0])
                    df = pd.json_normalize(postal_code_list[0])
                    return df['long_name'].astype(str).iloc[0]
            else:
                return None
        else:
            return None

    def enrich_with_postal_code(self, row):
        outlet_name = row.get('name')
        address_lat = row.get('lat')
        address_lng = row.get('long')

        print(
            f"Enriching postal code for {outlet_name} ({address_lat}, {address_lng})....")

        google_reverse_geocode_results = self.reverse_geocode_google(
            address_lat, address_lng)

        if google_reverse_geocode_results:
            print(
                f"Postal code for {outlet_name} (Google): {google_reverse_geocode_results}")
        else:
            print(
                f"Postal code for {outlet_name} (Google): No results")
        row['POSTALCODE_GOOGLE'] = google_reverse_geocode_results if google_reverse_geocode_results else 'No results'

        # Only if the TEXT_SEARCH_REGION is .sg, we will use the onemap API
        # Add new results to the row; if None, add 'No results'
        if key_parameters.TEXT_SEARCH_REGION == '.sg':
            # If time taken to get the postal code is too long, we need to move on to the next row

            reverse_geocode_results = self.reverse_geocode(
                address_lat, address_lng)
            if reverse_geocode_results:
                print(
                    f"Postal code for {outlet_name} (OneMap): {reverse_geocode_results}")
            else:
                print(f"Postal code for {outlet_name} (OneMap): No results")
            row['POSTALCODE'] = reverse_geocode_results if reverse_geocode_results else 'No results'
            time.sleep(key_parameters.REVERSE_GEOCODE_API_CALL_BUFFER_TIME)
            # I want to do a coalesce here, if the first one is None, then we use the second one for combined postal code
            row['POSTALCODE_COMBINED'] = row['POSTALCODE_GOOGLE'] if row['POSTALCODE_GOOGLE'] != 'No results' else row['POSTALCODE']
            return row

        return row

    def main_get_postal_code(self, combined_area_point_df):
        print(
            f"############ Starting Postal Code search.... ############\n")
        a = combined_area_point_df.apply(
            self.enrich_with_postal_code, axis=1)
        if key_parameters.TEXT_SEARCH_REGION == '.sg':
            a.loc[:, 'POSTALCODE'] = a['POSTALCODE'].astype(str)
            # This removes all rows where outlets are in JB
            a = a[a['POSTALCODE'] != 'NIL']
        a.to_csv(os.path.join(output_folder_path, f'primary_data_with_postal_code_{key_parameters.NEARBY_SEARCH_TYPE}.csv'), index=False)

    def get_place_details_helper(self, row):
        # get place details for the row, add place_id into the payload
        # query the place details from the google maps API
        place_id = row.get('place_id')
        self.google_maps_place_details_payload['place_id'] = place_id
        response = requests.get(
            google_maps_place_details_url, params=self.google_maps_place_details_payload)
        response = response.json()
        result = response.get('result', {})
        # print(result)
        # print(result.get('formatted_phone_number', ''))
        row['formatted_phone_number'] = result.get(
            'formatted_phone_number', '') if result.get('formatted_phone_number', '') else 'No results'
        row['international_phone_number'] = result.get(
            'international_phone_number', '') if result.get('international_phone_number', '') else 'No results'
        print(
            f"Contact details for {row.get('outlet_name')}: {row.get('formatted_phone_number')}")
        return row
    
    def get_place_details(self, quality_leads_df):
        print(
            f"############ Starting Place Details search.... ############\n")
        # This is to get the contact details of the most high quality places
        quality_leads_df.loc[:, 'place_id'] = quality_leads_df['place_id'].astype(str)
        a = quality_leads_df.apply(
            self.get_place_details_helper, axis=1)
        return a
        # a.to_csv(os.path.join(output_folder_path, 'with_ratings_and_.csv'), index=False)
    


