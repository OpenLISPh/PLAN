import os

from dotenv import load_dotenv

# Path to .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")

# Check if .env file exists
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Missing .env file at {env_path}")

# Load .env file
load_dotenv()

# Define environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
