class Config:
    # Example connection string for SQL Server
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://sa1:1234@./DW_Monoprix?driver=ODBC+Driver+17+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # New MongoDB settings
    MONGO_URI = "mongodb://localhost:27017/Users"

    # Session token
    SECRET_KEY = "your_super_secret_key"  # Change en prod !
    JWT_EXPIRATION_SECONDS = 86400  # 1 jour (en secondes)
