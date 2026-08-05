import os

API_KEY = os.getenv("API_KEY", "dev-insecure-key")
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
