from flask import Flask, jsonify, request, abort, send_file
from pymongo import MongoClient
from flask_cors import CORS
import uuid

# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Route to serve index.html
@app.route('/')
def serve_index():
    return send_file('index.html')

# MongoDB connection (update with your own connection string)
client = MongoClient('mongodb+srv://zarathustrant:aCRmg2RAJcpoWMKo@aerys.lmphm.mongodb.net/?retryWrites=true&w=majority&appName=Aerys')
db = client['Pipeline']  # Replace with your database name
collection = db['Features']  # Replace with your collection name

# Helper function to convert MongoDB ObjectID to string
def format_feature(feature):
    feature['_id'] = str(feature['_id'])
    return feature

# Route to fetch all features
@app.route('/features', methods=['GET'])
def get_features():
    features = list(collection.find())
    return jsonify([format_feature(feature) for feature in features]), 200

# Route to fetch a single feature by ID
@app.route('/features/<string:feature_id>', methods=['GET'])
def get_feature(feature_id):
    feature = collection.find_one({"_id": feature_id})
    if feature:
        return jsonify(format_feature(feature)), 200
    else:
        abort(404, description="Feature not found")

# Route to add a new feature
@app.route('/features', methods=['POST'])
def add_feature():
    data = request.json

    # Create a new feature with a unique ID
    new_feature = {
        "_id": str(uuid.uuid4()),  # Generate a unique ID
        "type": data.get("type", "Feature"),
        "properties": data.get("properties", {}),
        "geometry": data.get("geometry", {})
    }

    # Insert the feature into MongoDB
    collection.insert_one(new_feature)
    
    return jsonify(format_feature(new_feature)), 201

# Route to update a feature by ID (PUT)
@app.route('/features/<id>', methods=['PUT'])
def update_feature(id):
    data = request.json  # Get the JSON data from the request
    updated_properties = data.get("properties", {})  # Extract the updated properties from the request

    if not updated_properties:
        return jsonify({"error": "No properties provided"}), 400

    try:
        # Update the feature in the database
        result = mongo.db.features.update_one(
            {"_id": ObjectId(id)},  # Match by the feature's MongoDB ObjectId
            {"$set": {"properties": updated_properties}}  # Update the properties field
        )

        if result.matched_count == 0:
            return jsonify({"error": "Feature not found"}), 404

        return jsonify({"message": "Feature updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a feature by ID
@app.route('/features/<string:feature_id>', methods=['DELETE'])
def delete_feature(feature_id):
    result = collection.delete_one({"_id": feature_id})

    if result.deleted_count == 1:
        return jsonify({"message": "Feature deleted successfully"}), 200
    else:
        abort(404, description="Feature not found")

