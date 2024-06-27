# Before running script for Project Crobat
1.) Run `pip install -r requirements.txt` to get all the required python packages\
2.) Create your own `api_secrets.py` file to access Google and OneMap API using `api_secrets_template.py`\
3.) Check `key_parameters.py` for:\
    &ensp; a.) Parameter inputs for the respective API payloads. For required inputs by Google Maps API view [Project documentation](https://docs.google.com/document/d/1LMR_PapF468NU_nVOSQTbVeaDbuT1D0ERhoEOWYHWIM/edit)\
    &ensp; b.) Columns you want to return and column renaming. For list of columns that Google API will return: https://docs.google.com/document/d/1LMR_PapF468NU_nVOSQTbVeaDbuT1D0ERhoEOWYHWIM/edit#bookmark=id.ayiz52nuepcx\
    &ensp; c.) USER in key_parameters (use 'test' to test if you've set everything up properly before querying the entire dataset in `combined_data.xlsx`, this will run all the APIs for 1 Mall and 1 Busstop) 
