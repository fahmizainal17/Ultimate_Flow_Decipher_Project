import pandas as pd
import numpy as np
from typing import List, Tuple

def merger(df_list: List[pd.DataFrame], phonenum_list: List[pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Concatenates lists of DataFrames and renames a column.

    Parameters:
    - df_list (list of pd.DataFrame): List of DataFrames to be concatenated vertically.
    - phonenum_list (list of pd.DataFrame): List of phone number DataFrames to be concatenated vertically.

    Returns:
    - df_merge (pd.DataFrame): Concatenated DataFrame of df_list.
    - phonenum_combined (pd.DataFrame): Concatenated DataFrame of phonenum_list with 'PhoneNo' column renamed to 'phonenum'.
    """
    # Check if the lists are not empty before concatenating
    if df_list:
        df_merge = pd.concat(df_list, axis='index')
    else:
        df_merge = pd.DataFrame()  # Return an empty DataFrame if list is empty

    if phonenum_list:
        phonenum_combined = pd.concat(phonenum_list, axis='rows')
        phonenum_combined.rename(columns={'PhoneNo': 'phonenum'}, inplace=True)
    else:
        phonenum_combined = pd.DataFrame()  # Return an empty DataFrame if list is empty

    return df_merge, phonenum_combined

def process_file(uploaded_file: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, int, int, pd.DataFrame]:
    """
    Process the uploaded CSV file to extract and transform phone number data
    and user response data for analysis.

    The function performs several steps:
    - Reads the CSV, skipping the first row and setting column names dynamically.
    - Drops columns that are entirely NA.
    - Extracts columns for phone numbers and user responses.
    - Identifies total number of calls and total pickups.
    - Filters data to complete responses where a user key press is recorded.
    - Adds a 'Set' column to indicate data belonging to the IVR set.
    - Filters for records where the user key press response is exactly 10 characters long.

    Parameters:
    - uploaded_file: A file-like object representing the uploaded CSV file.
                     This object must support file-like operations such as read.

    Returns:
    - A tuple containing:
        - df_complete: A pandas DataFrame of the processed data, with calls that have complete information.
        - phonenum_combined: A pandas DataFrame containing the list of phone numbers that have at least one user key press.
        - total_calls_made: The total number of calls (rows) in the uploaded file.
        - total_of_pickups: The total number of calls where a user key press was recorded.
        - df_merge: The concatenated DataFrame of all processed data.
    """
    df_list = []
    phonenum_list = []
    total_calls = []
    total_calls_made = []
    total_pickup = []
    total_of_pickups = []

    df = pd.read_csv(uploaded_file, skiprows=1, names=range(100), engine='python')

    df.dropna(axis='columns', how='all', inplace=True)

    df.columns = df.iloc[0]

    df_phonenum = df[['PhoneNo']]
    df_response = df.loc[:, 'UserKeyPress':]
    df_results = pd.concat([df_phonenum, df_response], axis='columns')
    
    df_results.drop_duplicates(subset=['PhoneNo'], inplace=True)
    total_calls_made = len(df_results)
    total_calls.append(total_calls_made)
    
    phonenum_recycle = df_results.dropna(subset=['UserKeyPress'])

    phonenum_list = phonenum_recycle[['PhoneNo']]
    
    df_complete = df_results.dropna(axis='index')

    total_of_pickups = len(df_complete)
    total_pickup.append(total_of_pickups)

    df_complete.columns = np.arange(len(df_complete.columns))

    df_complete['Set'] = 'IVR'
    df_complete = df_complete.loc[:, :'Set']

    df_complete = df_complete.loc[(df_complete.iloc[:, 2].str.len() == 10)]

    df_list.append(df_complete)
    
    df_list = pd.DataFrame
    # Call the merger function at the end of process_file to merge df_list and phonenum_list
    df_merge, phonenum_combined = merger([df_complete], [phonenum_list])  # Adjusted to pass lists of DataFrames

    # Correct the return statement to include all expected return values
    return df_complete, phonenum_combined, total_calls_made, total_of_pickups, df_merge, df_list