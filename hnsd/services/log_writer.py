from typing import Any, Dict
import json
from pathlib import Path
            
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path



class LogWriter(logging.Logger):
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def write(
        self, 
        result: Dict[str, Any]
        ) -> None:
        with open(self.log_path, "a") as f:
            f.write(result + "\n")

def setup_logger(name: str, log_path: Path, when="midnight", backup_count=7) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = TimedRotatingFileHandler(str(log_path), when=when, backupCount=backup_count)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    return logger
