from typing import List, Dict, Type, TypeVar
import pandas as pd
from pydantic import ValidationError


def convert_dataframe_to_pydantic(
    df: pd.DataFrame,
    model,
    field_mapping: Dict[str, str]) -> List:
    """
    Converts a Pandas DataFrame to a list of Pydantic models with field remapping.

    Args:
        df: The input Pandas DataFrame.
        model: The Pydantic model class to convert to.
        field_mapping: A dictionary to map DataFrame column names to Pydantic model field names.
                       Example: {'dataframe_column_name': 'pydantic_field_name'}

    Returns:
        A list of Pydantic model instances.
    """
    # Rename the columns of the dataframe based on the provided mapping
    df_renamed = df.rename(columns=field_mapping)
    print(df_renamed.columns)

    # Convert the DataFrame to a list of dictionaries
    records = df_renamed.to_dict(orient='records')

    # Create a list to store the Pydantic model instances
    model_instances = []
    # Iterate over the records and create Pydantic model instances
    for i, record in enumerate(records):
        # try:
            
        record = {k:v for k,v in record.items() if k in model.model_json_schema()['properties'].keys()}
        
        # Hardcode overwrite here for now.
        # Refactor this for later on to help with the tags and handling of the tag table
        record['tags'] = list()
        model_instance = model(**record)
        model_instances.append(model_instance)
        # except ValidationError as e:
        #     # Handle validation errors, e.g., print an error message
        #     print(f"Validation error for row {i}: {e}")
        #     # You might want to skip the row, or handle it in another way
        #     continue

    return model_instances