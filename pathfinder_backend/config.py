import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Keys
PRIVATE_KEY_PATH = BASE_DIR / "private_key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "public_key.pem"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/pathfinder.db")

# Policies file
POLICY_FILE = os.getenv("POLICY_FILE", "policies.yaml")

# Default policy version
DEFAULT_POLICY_VERSION = "1.0.0"