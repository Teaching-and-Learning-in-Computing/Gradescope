# utils.py

import json
import dataclasses
import pandas as pd


class EnhancedJSONEncoder(json.JSONEncoder):
    '''
    A custom JSON encoder that supports encoding dataclasses as dictionaries.
    '''

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def load_json(path: str) -> dict:
    '''
    Load JSON data from a file.

    Args:
        path: The path to the JSON file.

    Returns:
        The loaded JSON data as a dictionary.
    '''
    with open(path, 'r') as file:
        return json.load(file)


def save_json(path: str, data: dict, indent: int = 4, encoder: json.JSONEncoder | None = EnhancedJSONEncoder) -> None:
    '''
    Save JSON data to a file.

    Args:
        path: The path to save the JSON file.
        data: The data to be saved as JSON.
        indent: The number of spaces to use for indentation (default is 4).
        encoder: The JSON encoder to use (default is EnhancedJSONEncoder).

    Returns:
        None
    '''
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent, cls=encoder)


def load_csv(path: str) -> pd.DataFrame:
    '''
    Load CSV data from a file.

    Args:
        path: The path to the CSV file.

    Returns:
        The loaded CSV data as a pandas DataFrame.
    '''
    return pd.read_csv(path)


def save_csv(path: str, dataframe: pd.DataFrame, index: bool = False) -> None:
    '''
    Save DataFrame data to a CSV file.

    Args:
        path: The path to save the CSV file.
        dataframe: The DataFrame to be saved.
        index: Whether to include the index in the CSV file (default is False).

    Returns:
        None
    '''
    dataframe.to_csv(path, index=index)
