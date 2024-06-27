# This script is mainly to get the contact details from the culmulative dataset
# Idea:
# Input a culmulative dataset, and get the contact details of the places
# Filter for records with place_id
# Filter for predefined values of # of reviews and rating

from Crobat import Crobat
from search_classes.AreaSearch import AreaSearch
from search_classes.PointSearch import PointSearch
from LocationSplitter import LocationSplitter
import api_secrets
import key_parameters
import pandas as pd
import numpy as np
from datetime import datetime
import os
import key_parameters

startTime = datetime.now()
output_folder_path = key_parameters.OUTPUT_FOLDER_PATH
os.makedirs(output_folder_path, exist_ok=True)
# Asks users for their information through inputs
google_map_api_key = api_secrets.GOOGLE_MAP_API_KEY
onemap_email = api_secrets.ONEMAP_EMAIL
onemap_password = api_secrets.ONEMAP_PASSWORD
user = key_parameters.USER

# Load the excel file containing the mall and busstop data
primary_data_with_ratings = key_parameters.PRIMARY_DATA_WITH_RATINGS
locations = pd.read_csv(primary_data_with_ratings)

crobat = Crobat(google_map_api_key, onemap_email, onemap_password)
# Filter for the quality locations
# filtered_locations = locations[(locations['outlet_ratings'] >= key_parameters.NUMBER_OF_RATINGS_FILTER &
#                                # and there is a place_id
#                                locations['place_id'].notnull())
#                                # or
#                                # df_1 = df[df['POSTALCODE'].str.startswith('33') | df['POSTALCODE'].str.startswith('34') | df['POSTALCODE'].str.startswith('26') | df['POSTALCODE'].str.startswith('59')]
#                                 (locations['POSTALCODE'].str.startswith('33') | locations['POSTALCODE'].str.startswith('34') | locations['POSTALCODE'].str.startswith('26') | locations['POSTALCODE'].str.startswith('59'))]

non_null_place_id = locations[locations['place_id'].notnull()]
filtered_locations = non_null_place_id[(non_null_place_id['outlet_ratings'] >= key_parameters.NUMBER_OF_RATINGS_FILTER)
                                        # or the postal code starts with 33, 34, 26, 59
                                        | (non_null_place_id['POSTALCODE'].str.startswith('33') | non_null_place_id['POSTALCODE'].str.startswith('34') | non_null_place_id['POSTALCODE'].str.startswith('26') | non_null_place_id['POSTALCODE'].str.startswith('59'))]
# print the number of locations that are filtered
print(f"Number of locations filtered: {len(filtered_locations)}")

# LocationSplitter splits the filtered data into # of people assigned
location_splitter = LocationSplitter(filtered_locations, key_parameters.USER)
location_splitter.simple_split(key_parameters.NUMBER_OF_USERS)
df = location_splitter.select_data(key_parameters.LIMIT_POSTAL_CODE_DATA)
crobat.load_api_payloads('google_maps_place_details',
                         fields=key_parameters.PLACE_DETAILS_DATA)
# Then enhances the split data to get the contact details
enhanced_with_contact = crobat.get_place_details(df)
enhanced_with_contact.to_csv(os.path.join(
    output_folder_path, f'with_ratings_contact_info.csv'), index=False)
print(f"\n############ Time taken: {datetime.now() - startTime} ############")
