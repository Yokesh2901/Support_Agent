# src/memory/memory_bank.py
import json, os
from typing import List

class MemoryBank:
    PATH = "memory_bank.json"

    def __init__(self):
        if not os.path.exists(self.PATH):
            self._write([])

    def _read(self) -> List[dict]:
        with open(self.PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: List[dict]):
        with open(self.PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save(self, record: dict):
        data = self._read()
        data.append(record)
        self._write(data)

    def all(self) -> List[dict]:
        return self._read()
