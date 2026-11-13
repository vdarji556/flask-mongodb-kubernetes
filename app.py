
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection
host = os.getenv("MONGO_HOST", "localhost")
port = os.getenv("MONGO_PORT", "27017")
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")

if username and password:
    mongo_uri = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}"
        f"@{host}:{port}/?authSource={auth_source}"
    )
else:
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

db = client["flask_db"]
collection = db["data"]


@app.route("/")
def home():
    current_time = datetime.now()
    return f"Welcome to the Flask app! The current time is: {current_time}"


@app.route("/healthz")
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"status": "database connection failed"}), 503


@app.route("/data", methods=["GET", "POST"])
def handle_data():

    if request.method == "POST":
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Valid JSON required"}), 400

        try:
            collection.insert_one(data)
            return jsonify({"status": "Data inserted"}), 201
        except Exception:
            return jsonify({"error": "Unable to insert data"}), 500

    try:
        records = list(collection.find({}, {"_id": 0}))
        return jsonify(records), 200
    except Exception:
        return jsonify({"error": "Unable to fetch data"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
