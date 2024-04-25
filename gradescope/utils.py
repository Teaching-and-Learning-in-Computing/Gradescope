# utils.py

import json
import dataclasses
import pandas as pd


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def load_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


def save_json(path: str, data: dict, indent: int = 4, encoder: json.JSONEncoder | None = EnhancedJSONEncoder) -> None:
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent, cls=encoder)


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def save_csv(path: str, dataframe: pd.DataFrame, index: bool = False) -> None:
    dataframe.to_csv(path, index=index)
