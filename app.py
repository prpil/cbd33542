import os
import pyodbc
import logging
from flask import Flask, request, redirect, url_for, flash, render_template
from google.cloud import storage

app = Flask(__name__)
app.secret_key = 'my_key'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Google Cloud Storage client
try:
    storage_client = storage.Client()
    logging.info("Connected to Google Cloud Storage")
except Exception as e:
    logging.error(f"Error connecting to Google Cloud Storage: {e}")

# Fetch the bucket name from the environment variable 'GCS_BUCKET_NAME'
bucket_name = os.getenv('GCS_BUCKET_NAME')
if not bucket_name:
    logging.error("Bucket name not set in environment variable 'GCS_BUCKET_NAME'")
    raise ValueError("Bucket name not set in environment variable 'GCS_BUCKET_NAME'")

try:
    bucket = storage_client.bucket(bucket_name)
except Exception as e:
    logging.error(f"Error accessing bucket: {e}")

# Database connection configuration
server = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
driver = '{ODBC Driver 17 for SQL Server}'


def test_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER=tcp:{server},1433;DATABASE={database};UID={username};PWD={password};Timeout=30')
        logging.info("Database connection successful")
        conn.close()
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")


def insert_file_record(filename, file_url):
    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER=tcp:{server},1433;DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=yes;')
        cursor = conn.cursor()

        insert_query = "INSERT INTO uploads (filename, file_url) VALUES (?, ?)"
        cursor.execute(insert_query, (filename, file_url))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"File record inserted into the database: {filename}, {file_url}")
    except Exception as e:
        logging.error(f"Error inserting record into the database: {e}")


# Route for uploading the file
@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            logging.warning("No file part in the request")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            logging.warning("No file selected")
            return redirect(request.url)

        if file:
            try:
                blob = bucket.blob(file.filename)
                blob.upload_from_file(file.stream)

                file_url = blob.public_url

                # Insert file record into the database
                insert_file_record(file.filename, file_url)

                flash('File successfully uploaded and saved to the database', 'success')
                logging.info(f"File {file.filename} uploaded successfully")
            except Exception as e:
                flash(f"Error uploading the file or saving to the database: {e}", 'error')
                logging.error(f"Error during file upload or database operation: {e}")

            return redirect(url_for('upload_file'))

    return render_template('upload.html')


# Run the app
if __name__ == '__main__':
    test_db_connection()
    app.run(host='0.0.0.0', port=8080)
