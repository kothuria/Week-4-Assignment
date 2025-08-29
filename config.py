from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    API_URL: str = os.getenv("API_URL", "https://example.com/api/send-confirmation")
    API_KEY: str = os.getenv("API_KEY", "DEMO_KEY")
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "25"))
    WORKERS: int = int(os.getenv("WORKERS", "8"))
