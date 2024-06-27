# either any string value (eg. test) or the index of the user (ie if there are 3 users, the index will be 1, 2, 3)
USER = 1
NUMBER_OF_USERS = 3  # This is the number of users
# Change to your output folder path, just use the same path as main.py, with output_files at the end
OUTPUT_FOLDER_PATH = '/Users/benjamin.wang.int/crobat-gmap-scraper/output_files'
# Change to your input folder path, just use the same path as main.py, with input_files at the end
INPUT_FOLDER_PATH = '/Users/benjamin.wang.int/crobat-gmap-scraper/input_files'

# This is the buffer time between each API call
REVERSE_GEOCODE_API_CALL_BUFFER_TIME = 60 / 240

# Text search payloads
TEXT_SEARCH_REGION = '.sg'  # This is the region of search to search for AREAs
# This is the centre of the region of search to search for AREAs
TEXT_SEARCH_LOCATION = '1.3521,103.8198'
# This is the search radius in the region to search for AREAs
TEXT_SEARCH_RADIUS = 50000

# AREA nearby search payloads
# This is the radius of search for each search circle in a AREA
AREA_CIRCLE_NEARBY_SEARCH_RADIUS = 150
# This is equivelent to AREA_CIRCLE_NEARBY_SEARCH_RADIUS - (radius used to determine number of circles in a AREA)
AREA_SEARCH_RADIUS_BUFFER = 50
AREA_CIRCLE_NEARBY_SEARCH_CALL_CAP = 3

# POINT nearby search payloads
# This is the radius of search for each search circle at a POINT / any point of interest that does not require calculations similar to AREAs
POINT_CIRCLE_NEARBY_SEARCH_RADIUS = 400
POINT_CIRCLE_NEARBY_SEARCH_CALL_CAP = 1

# This is the type of place to search. Refer to README to see the list of types available
NEARBY_SEARCH_TYPE = "bar"

# OneMap API payloads
# This is the radius of search for each search circle at a POINT
ONEMAP_BUFFER_RADIUS = 500
ONEMAP_ADDRESS_TYPE = 'All'  # This is the type of address to search for
ONEMAP_OTHER_FEATURES = 'N'  # This is the other features to search for

FINAL_COLUMNS = ['business_status', 'name', 'place_id', 'rating', 'types', 'user_ratings_total',
                 'vicinity', 'Location', 'Type', 'geometry.location.lat', 'geometry.location.lng', 'price_level']

# This is to rename the columns to the FINAL_COLUMNS
COLUMN_MAPPING = {
    'geometry.location.lat': 'lat',
    'geometry.location.lng': 'long'
}

COMBINED_DATA = '/Users/benjamin.wang.int/crobat-gmap-scraper/input_files/combined_data.xlsx'
# This is needed for the main_get_postal_code function to get the postal code
PRIMARY_DATA = f'/Users/benjamin.wang.int/crobat-gmap-scraper/input_files/combined_primary_data_{NEARBY_SEARCH_TYPE}.csv'

# This file is to contain Google outlets that are not in SB database, and are quality places to get contact details
# This is needed to get the contact details of the most high quality places
PRIMARY_DATA_WITH_RATINGS = f'/Users/benjamin.wang.int/crobat-gmap-scraper/input_files/with_ratings.csv'
PLACE_DETAILS_DATA = 'formatted_phone_number,international_phone_number'
NUMBER_OF_RATINGS_FILTER = 100
RATINGS_FILTER = 4.0
# This limits the number of rows passed in to both search classes
LIMIT_COMBINED_DATA = None
# This limits the number of rows passed in to the main_get_postal_code function, else None
LIMIT_POSTAL_CODE_DATA = None

FILENAME_DICT = {
    # The file sequence should be as follows:
    # The next 2 files are to combine the data from different people
    'main_run_dedup': f'combined_primary_data_{NEARBY_SEARCH_TYPE}.csv',
    'postal_code_run_dedup': f'combined_primary_data_with_postal_code_{NEARBY_SEARCH_TYPE}.csv',
    'dfs_dedup_merge': 'combined_primary_data_with_postal_code_culmulative.csv', # This is to combine the data from the different runs (restaraunt, bar, etc.)
    # This file is also used to replace rows with the same place_id in a csv with the contact details filled in
    'contact_details_run_dedup': 'combined_filtered_data_with_postal_code_contact_details.csv' # This file is to combine the data from different people after getting the postal code, done matching and gotten contact details
}
