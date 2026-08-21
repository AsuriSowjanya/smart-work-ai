import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL found:", bool(DATABASE_URL))

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("PostgreSQL connection successful!")
        print("Result:", result.scalar())

except Exception as e:
    print("PostgreSQL connection failed:")
    print(e)