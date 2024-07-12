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

startTime = datetime.now()
csv_time = datetime.now().isoformat(sep=" ")

output_folder_path = key_parameters.OUTPUT_FOLDER_PATH
os.makedirs(output_folder_path, exist_ok=True)


def main_combine_area_point_data(source_places__area_df, source_stats__area_df, source_search_circles_area, source_places__point_df, source_stats__point_df):
    # I want it to be such that if we ran only areas, then we set combined_area_point_df to only areas data, and vice versa

    combined_area_point_df = pd.concat(
        [source_places__area_df, source_places__point_df],
        ignore_index=True
    )

    combined_area_point_stats_df = pd.concat(
        [source_stats__area_df, source_stats__point_df],
        ignore_index=True
    )

    #### Data Filtering ####
    # We want to keep the outlet from areas should there be duplicates
    dedup_area_point_df = combined_area_point_df.drop_duplicates(
        subset='place_id', keep='first')
    # Get only operational outlets
    source_places__area_point_df = dedup_area_point_df.loc[
        dedup_area_point_df['business_status'] == "OPERATIONAL"]
    # Get only the columns that we want
    final_columns__area_point = source_places__area_point_df[
        key_parameters.FINAL_COLUMNS]
    column_mapping = key_parameters.COLUMN_MAPPING
    # List of columns to extract from 'final_df'
    combined_area_point_df = final_columns__area_point.rename(
        columns=column_mapping)
    # Drop rows with missing values in user_ratings_total
    combined_area_point_df = combined_area_point_df.dropna(
        subset=['user_ratings_total'])
    ########################

    combined_area_point_df.to_csv(os.path.join(
        output_folder_path, f'primary_data_{key_parameters.NEARBY_SEARCH_TYPE}.csv'), index=False)
    combined_area_point_stats_df.to_csv(
        os.path.join(output_folder_path, f'stats_data_{key_parameters.NEARBY_SEARCH_TYPE}.csv'), index=False)
    source_search_circles_area.to_csv(
        os.path.join(output_folder_path, f'area_search_circles_{key_parameters.NEARBY_SEARCH_TYPE}.csv'), index=False)

    return combined_area_point_df


# Asks users for their information through inputs
google_map_api_key = api_secrets.GOOGLE_MAP_API_KEY
onemap_email = api_secrets.ONEMAP_EMAIL
onemap_password = api_secrets.ONEMAP_PASSWORD
user = key_parameters.USER
# Load the excel file containing the mall and busstop data
combined_data = key_parameters.COMBINED_DATA
location_types = pd.read_excel(combined_data)['Type'].unique()

# Get the different location types from Type column in the mall_plus_busstops, and store them in a list
location_data_by_type = {}

for location_type in location_types:
    # User location splitter and split
    location_splitter = LocationSplitter(combined_data, key_parameters.USER)
    location_splitter.split(key_parameters.NUMBER_OF_USERS, location_type)
    location_data_by_type[location_type] = location_splitter.select_data(key_parameters.LIMIT_COMBINED_DATA)

area_search = AreaSearch(
    google_map_api_key, location_data_by_type['AreaSearch'])
point_search = PointSearch(
    google_map_api_key, location_data_by_type['PointSearch'])

area_search.load_api_payloads('text_search', region=key_parameters.TEXT_SEARCH_REGION,
                              radius=key_parameters.TEXT_SEARCH_RADIUS, location=key_parameters.TEXT_SEARCH_LOCATION)
area_search.load_api_payloads('area_circle_nearby_search',
                              radius=key_parameters.AREA_CIRCLE_NEARBY_SEARCH_RADIUS)
point_search.load_api_payloads('point_nearby_search',
                               radius=key_parameters.POINT_CIRCLE_NEARBY_SEARCH_RADIUS)

source_places__area_df, source_stats__area_df, source_search_circles_area = area_search.main_search()
source_places__point_df, source_stats__point_df = point_search.main_search()
combined_area_point_df = main_combine_area_point_data(
    source_places__area_df, source_stats__area_df, source_search_circles_area, source_places__point_df, source_stats__point_df)
print(f"\n############ Time taken: {datetime.now() - startTime} ############")
