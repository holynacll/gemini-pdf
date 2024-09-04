import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.base_dir: Path = Path(__file__).parent.parent
        self.static_dir: Path = self.base_dir / "static"
        if not self.static_dir.exists():
            self.static_dir.mkdir(parents=True, exist_ok=True)
        self.google_api_key = os.environ["GOOGLE_API_KEY"]
        self.port = os.environ["PORT"]

# Instância global a ser importada
settings = Config()
