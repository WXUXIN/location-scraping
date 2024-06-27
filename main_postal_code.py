from Crobat import Crobat
from search_classes.AreaSearch import AreaSearch
from search_classes.PointSearch import PointSearch
from LocationSplitter import LocationSplitter
import api_secrets
import key_parameters
import pandas as pd
import numpy as np
from datetime import datetime
import key_parameters

startTime = datetime.now()
# Asks users for their information through inputs
google_map_api_key = api_secrets.GOOGLE_MAP_API_KEY
onemap_email = api_secrets.ONEMAP_EMAIL
onemap_password = api_secrets.ONEMAP_PASSWORD
user = key_parameters.USER

# Load the excel file containing the mall and busstop data
primary_data = key_parameters.PRIMARY_DATA
locations = pd.read_csv(primary_data)

crobat = Crobat(google_map_api_key, onemap_email, onemap_password)

location_splitter = LocationSplitter(primary_data, key_parameters.USER)
location_splitter.simple_split(key_parameters.NUMBER_OF_USERS)
df = location_splitter.select_data(key_parameters.LIMIT_POSTAL_CODE_DATA)

crobat.load_api_payloads('google_maps_reverse_geocode', region='.sg')
crobat.load_api_payloads('reverse_geocode', buffer=key_parameters.ONEMAP_BUFFER_RADIUS,
                         addressType=key_parameters.ONEMAP_ADDRESS_TYPE, otherFeatures=key_parameters.ONEMAP_OTHER_FEATURES)
crobat.load_api_payloads('reverse_geocode_header')
crobat.main_get_postal_code(df)
print(f"\n############ Time taken: {datetime.now() - startTime} ############")