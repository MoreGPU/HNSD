from typing import Any, Dict
import json
from pathlib import Path


class LogWriter:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def write(
        self, 
        result: Dict[str, Any]
        ) -> None:
        with open(self.log_path, "a") as f:
            f.write(result + "\n")