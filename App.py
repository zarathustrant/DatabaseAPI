from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
import uuid

# Initialize Flask app
app = Flask(__name__)

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

# Route to update an existing feature by ID (full or partial)
@app.route('/features/<string:feature_id>', methods=['PUT'])
def update_feature(feature_id):
    data = request.json

    # Find the feature by ID
    feature = collection.find_one({"_id": feature_id})
    if not feature:
        abort(404, description="Feature not found")

    # Prepare the updated feature with optional new data for each field
    updated_feature = {
        "type": data.get("type", feature["type"]),  # Update type if provided, else retain the old value
        "properties": {  # Update individual properties if provided
            "Feature Type": data.get("properties", {}).get("Feature Type", feature["properties"].get("Feature Type")),
            "Status": data.get("properties", {}).get("Status", feature["properties"].get("Status")),
            "Operator": data.get("properties", {}).get("Operator", feature["properties"].get("Operator")),
            "Last Inspection Date": data.get("properties", {}).get("Last Inspection Date", feature["properties"].get("Last Inspection Date")),
            # You can add more fields here for specific attributes
        },
        "geometry": data.get("geometry", feature["geometry"])  # Update geometry if provided
    }

    # Perform the update in MongoDB
    collection.update_one({"_id": feature_id}, {"$set": updated_feature})

    # Fetch the updated feature and return
    updated_feature = collection.find_one({"_id": feature_id})
    return jsonify(format_feature(updated_feature)), 200

# Route to delete a feature by ID
@app.route('/features/<string:feature_id>', methods=['DELETE'])
def delete_feature(feature_id):
    result = collection.delete_one({"_id": feature_id})

    if result.deleted_count == 1:
        return jsonify({"message": "Feature deleted successfully"}), 200
    else:
        abort(404, description="Feature not found")

