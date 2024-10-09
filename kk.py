import os
import pyodbc
from flask import Flask, request, redirect, url_for, flash, render_template_string
from google.cloud import storage

app = Flask(__name__)
app.secret_key = 'my_key'

# Initialize Google Cloud Storage client
try:
    storage_client = storage.Client()
    print("Connected to Google Cloud Storage")
except Exception as e:
    print(f"Error connecting to Google Cloud Storage: {e}")

# Fetch the bucket name from the environment variable 'GCS_BUCKET_NAME'
bucket_name = os.getenv('GCS_BUCKET_NAME')
if not bucket_name:
    raise ValueError("Bucket name not set in environment variable 'GCS_BUCKET_NAME'")
try:
    bucket = storage_client.bucket(bucket_name)
except Exception as e:
    print(f"Error accessing bucket: {e}")

# Database connection configuration
server = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
driver = '{ODBC Driver 18 for SQL Server}'
driver = '{ODBC Driver 17 for SQL Server}'

def test_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER=tcp:{server},1433;DATABASE={database};UID={username};PWD={password};Timeout=30')
        print("Database connection successful")
        conn.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")


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
    except Exception as e:
        print(f"Error inserting record into the database: {e}")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file:
            try:
                blob = bucket.blob(file.filename)
                blob.upload_from_file(file.stream)

                file_url = blob.public_url

                insert_file_record(file.filename, file_url)

                flash('File successfully uploaded and saved to the database', 'success')
            except Exception as e:
                flash(f"Error uploading the file or saving to the database: {e}", 'error')

            return redirect(url_for('upload_file'))

    return render_template_string('''
    <!doctype html>
    <title>Upload an Image</title>
    <h1>Upload an Image to GCP Bucket</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
          {% for category, message in messages %}
            <li class="{{ category }}">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method=post enctype=multipart/form-data>
      <input type=file name=file accept="image/*">
      <input type=submit value=Upload>
    </form>
    ''')


if __name__ == '__main__':
    test_db_connection()
    app.run(host='0.0.0.0', port=8080)

