# utils.py

import json


def load_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


def save_json(path: str, data: dict, indent: int = 4, encoder: json.JSONEncoder | None = None) -> None:
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent, cls=encoder)
