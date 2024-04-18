# utils.py

import json
import dataclasses


def load_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)


def save_json(path: str, data: dict, indent: int = 4, encoder: json.JSONEncoder | None = None) -> None:
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent, cls=encoder)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
