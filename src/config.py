from pathlib import Path


class Config:
    def __init__(self):
        self.base_dir: Path = Path(__file__).parent.parent
        self.static_dir: Path = self.base_dir / "static"
        if not self.static_dir.exists():
            self.static_dir.mkdir(parents=True, exist_ok=True)

# Instância global a ser importada
settings = Config()
