import pandas as pd
import numpy as np

class LocationSplitter:
    def __init__(self, source_data, user):
        if isinstance(source_data, pd.DataFrame):
            self.source_data = source_data
        else:
            try:
                self.source_data = pd.read_excel(source_data)
            except:
                self.source_data = pd.read_csv(source_data)
        self.main_df_list = []
        self.user = user

    # This split is for use in main script 
    def split(self, user_num, location_type):
        main_df = self.source_data[
            self.source_data['Type'] == location_type]
        self.main_df_list = np.array_split(main_df, user_num)

    # This split is for use in main_postal_code script
    def simple_split(self, user_num):
        self.main_df_list = np.array_split(self.source_data, user_num)
    
    def select_data(self, limit=None):
        if isinstance(self.user, str):
            return self.main_df_list[0].head(1)
        try:
            self.main_df_list[self.user - 1]
        except IndexError:
            print(f'User index {self.user} does not exist / Index is wrong')
            return None
        if limit is not None:
            return self.main_df_list[self.user  - 1].head(limit)
        return self.main_df_list[self.user - 1]
    
