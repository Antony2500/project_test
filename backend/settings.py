import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG: str = f"mysql+aiomysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


