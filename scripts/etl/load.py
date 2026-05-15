# The get_engine() function is responsible for creating and returning a connection to the MySQL database, based on the configuration information in the .env file, so that the entire Python pipeline (ETL, aggregation, Power BI preparation) can share a single database connection.

from sqlalchemy import create_engine
from dotenv import load_dotenv
import urllib.parse
import os

def get_engine():
    load_dotenv()
    # 👉 Load environment variables from the .env file into the system

    user = os.getenv("DB_USER", "root")
    # 👉 MySQL username
    # 👉 If the .env file contains DB_USER, use it
    # 👉 If not, the default is "root"

    password = os.getenv("DB_PASSWORD", "Ganpati1!")
    # 👉 MySQL Password
    # 👉 Leave blank if not set (for local developers)

    host = os.getenv("DB_HOST", "localhost")
    # 👉 MySQL server address
    # 👉 Usually localhost or IP/server name

    port = os.getenv("DB_PORT", "3306")
    # 👉 MySQL Port (default 3306)

    db = os.getenv("DB_NAME", "noodles_dw")
    # 👉 Name of the database to connect to
    # 👉 This database is where the data for Power BI is stored

    password = urllib.parse.quote_plus(password)
    # 👉 Encode password to avoid errors if there are special characters
    # 👉 Example: @ ! # $ %

    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}",
        echo=False, # 👉 Do not print SQL logs to the terminal
        pool_pre_ping=True, # 👉 Check your connection before querying (to avoid timeouts)
    )
    
    return engine
    # 👉 Returns the SQLAlchemy engine for other scripts to use.