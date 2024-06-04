import os

from dotenv import load_dotenv

PROJECT_ROOT = os.getcwd()
env_path = os.path.join(PROJECT_ROOT, ".env")

# Check if .env file exists
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Missing .env file at root {env_path}")

# Load .env file
load_dotenv(override=True)

# Define environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
GCP_MAPS_API_KEY = os.getenv("GCP_MAPS_API_KEY")
