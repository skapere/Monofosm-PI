import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{os.getenv('SQL_USERNAME')}:{os.getenv('SQL_PASSWORD')}@{os.getenv('SQL_SERVER')}/{os.getenv('SQL_DATABASE')}?driver={os.getenv('SQL_DRIVER').replace(' ', '+')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGO_URI = os.getenv("MONGO_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_EXPIRATION_SECONDS = 86400  # 1 day
