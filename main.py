from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Google Cloud Build with Flask!"

if __name__ == '__main__':
    # Use port 8080, which is standard for Google App Engine
    app.run(host='0.0.0.0', port=8080, debug=True)
