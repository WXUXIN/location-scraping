import pandas as pd
# import key_parameters from a file called key_parameters.py, which is in the a directory outside of the current directory
import key_parameters
import numpy as np  
import os

filename_dict = key_parameters.FILENAME_DICT

def dedup_function_new(type, **kwargs):
    combined_primary_area = pd.concat(kwargs.values(), ignore_index=True).drop_duplicates(subset='place_id', keep='first')
    filename = filename_dict.get(type, "unknown_merged_file.csv")
    combined_primary_area.to_csv(os.path.join(key_parameters.OUTPUT_FOLDER_PATH, filename), index=False)
  
def replace_with_contact_details(primary_data_with_ratings, enhanced_with_contact):
# This function aims to replace rows with the same place_id in primary_data_with_ratings csv with the contact details in enhanced_with_contact csv
  locations = pd.read_csv(primary_data_with_ratings)
  enhanced_with_contact = pd.read_csv(enhanced_with_contact)
  merged_df = pd.merge(locations, enhanced_with_contact, on='place_id', how='left', suffixes=('', '_new'))

  for column in locations.columns:
    if column != 'place_id':
      locations[column] = merged_df[column + '_new'].combine_first(merged_df[column])

  new_columns = enhanced_with_contact.columns.difference(locations.columns)
  for column in new_columns:
    locations[column] = merged_df[column]
  locations.to_csv(os.path.join(key_parameters.OUTPUT_FOLDER_PATH, f'combined_with_ratings_contact_info.csv'), index=False)

# Use dedup_function as a guide on how to use dedup_function_new, it shows the different file names from each member involved in the project
def dedup_function(type, **kwargs):
  if type == 'single_run_dedup':
    # d = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'primary_data_{key_parameters.NEARBY_SEARCH_TYPE}_ben.csv'))
    # e = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'primary_data_{key_parameters.NEARBY_SEARCH_TYPE}_zaki.csv'))
    # f = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'primary_data_{key_parameters.NEARBY_SEARCH_TYPE}_royce.csv'))

    combined_primary_area = pd.concat(
      kwargs.values(),
      ignore_index=True
    )

    dedup_combined_primary_area = combined_primary_area.drop_duplicates(
                subset='place_id', keep='first')

    dedup_combined_primary_area.to_csv(
        os.path.join(key_parameters.OUTPUT_FOLDER_PATH, f'combined_primary_data_{key_parameters.NEARBY_SEARCH_TYPE}.csv')
                , index=False)
    
  elif type == 'postal_code_run_dedup':
    # d = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'primary_data_with_postal_code_{key_parameters.NEARBY_SEARCH_TYPE}_ben.csv'))
    # e = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'primary_data_with_postal_code_{key_parameters.NEARBY_SEARCH_TYPE}_zaki.csv'))
    # f = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'primary_data_with_postal_code_{key_parameters.NEARBY_SEARCH_TYPE}_royce.csv'))

    combined_primary_area = pd.concat(
      kwargs.values(),
      ignore_index=True
    )

    dedup_combined_primary_area = combined_primary_area.drop_duplicates(
                subset='place_id', keep='first')

    dedup_combined_primary_area.to_csv(
        os.path.join(key_parameters.OUTPUT_FOLDER_PATH, f'combined_primary_data_with_postal_code_{key_parameters.NEARBY_SEARCH_TYPE}.csv')
                , index=False)
    
  elif type == 'dfs_dedup_merge':
    # I want to dedup the dataframes in **kwargs and merge them
    # print(kwargs.values())
    combined_primary_area = pd.concat(
      kwargs.values(),
      ignore_index=True
    )

    dedup_combined_primary_area = combined_primary_area.drop_duplicates(
                subset='place_id', keep='first')
    
    dedup_combined_primary_area.to_csv(
        os.path.join(key_parameters.OUTPUT_FOLDER_PATH, f'combined_primary_data_with_postal_code_culmulative.csv')
                , index=False)
    
  # Dedup before running API call for postal code
  elif type == 'between_run_dedup':
    # Merge for all the different API run data, and dedup
    g = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'combined_primary_data_cafe_og.csv'))
    h = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'combined_primary_data_restaurant.csv'))

    combined_primary_area = pd.concat(
      [g, h],
      ignore_index=True
    )

    dedup_combined_primary_area = combined_primary_area.drop_duplicates(
                subset='place_id', keep='first')

    dedup_combined_primary_area.to_csv(
        os.path.join(key_parameters.INPUT_FOLDER_PATH, f'combined_primary_data_cafe_restaurant.csv')
                , index=False)

# dedup_function_new('dfs_dedup_merge', 
              #  a = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'combined_primary_data_with_postal_code_bar.csv')),
              #  b = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'combined_primary_data_with_postal_code_culmulative.csv')))

# replace_with_contact_details(
#     os.path.join(key_parameters.INPUT_FOLDER_PATH, 'with_ratings.csv'),
#     os.path.join(key_parameters.INPUT_FOLDER_PATH, 'combined_filtered_data_with_postal_code_contact_details.csv')
# )

# 
df = pd.read_csv(os.path.join(key_parameters.INPUT_FOLDER_PATH, f'with_ratings.csv'))
# Find the values of POSTALCODE of length 5

# df_1 = df[df['POSTALCODE'].str.len() == 5]
# Find the rows with POSTALCODE that starts with 0
# df_1 = df[df['POSTALCODE'].str.startswith('0')]
# df_1.to_csv(os.path.join(key_parameters.OUTPUT_FOLDER_PATH, f'with_5_digits.csv'), index=False)

# 33- Lavender
# 34- Potong Pasir
# 26- Bukit Timah
# 59- King Albert park/Bukit Timah
# Find the rows with POSTALCODE that starts with 33, 34, 26, 59
# df_1 = df[df['POSTALCODE'].str.startswith('33') | df['POSTALCODE'].str.startswith('34') | df['POSTALCODE'].str.startswith('26') | df['POSTALCODE'].str.startswith('59')]
# df_1.to_csv(os.path.join(key_parameters.OUTPUT_FOLDER_PATH, f'with_33_34_26_59.csv'), index=False)