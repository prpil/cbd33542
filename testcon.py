import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Database connection configuration using environment variables
server = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
driver = '{ODBC Driver 18 for SQL Server}'  # Ensure this is the correct driver version


# Function to test the database connection
def test_db_connection():
    try:
        # Attempt to establish the connection to the SQL Server
        connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(connection_string)

        print("Connection to the database was successful!")

        # Execute a simple query to verify the connection further
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("Database query executed successfully!")
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")


if __name__ == "__main__":
    test_db_connection()
