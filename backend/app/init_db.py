"""Create the schema and load seed data: `python -m app.init_db`."""

from app.config import DATABASE_URL
from app.db import reset_database

if __name__ == "__main__":
    reset_database()
    print(f"Database ready at {DATABASE_URL.rsplit('@', 1)[-1]}")
