from flask import Flask, jsonify, request, abort, send_file
import json
import os
import uuid
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Path to the JSON file in the root directory
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'kaduna_piipeline.json')

# Helper function to load the JSON data from file
def load_json_data():
    with open(JSON_FILE_PATH, 'r') as file:
        return json.load(file)

# Helper function to save the JSON data to file
def save_json_data(data):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

# Helper function to find a feature by ID
def find_feature_by_id(features, feature_id):
    for feature in features:
        if feature["_id"] == feature_id:
            return feature
    return None

# Route to serve index.html
@app.route('/')
def serve_index():
    return send_file('index.html')

# Route to fetch all features (GET)
@app.route('/features', methods=['GET'])
def get_features():
    try:
        # Load data from JSON file
        data = load_json_data()
        return jsonify(data["features"]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch a single feature by ID (GET)
@app.route('/features/<string:feature_id>', methods=['GET'])
def get_feature(feature_id):
    try:
        # Load data from JSON file
        data = load_json_data()
        feature = find_feature_by_id(data["features"], feature_id)
        if feature:
            return jsonify(feature), 200
        else:
            abort(404, description="Feature not found")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add a new feature (POST)
@app.route('/features', methods=['POST'])
def add_feature():
    try:
        # Load data from JSON file
        data = load_json_data()
        new_feature = {
            "_id": str(uuid.uuid4()),  # Generate a unique ID
            "type": request.json.get("type", "Feature"),
            "properties": request.json.get("properties", {}),
            "geometry": request.json.get("geometry", {})
        }
        data["features"].append(new_feature)

        # Save the updated data back to the JSON file
        save_json_data(data)
        return jsonify(new_feature), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update a feature by ID (PUT)
@app.route('/features/<string:feature_id>', methods=['PUT'])
def update_feature(feature_id):
    try:
        # Load data from JSON file
        data = load_json_data()
        updated_properties = request.json.get("properties", {})

        if not updated_properties:
            return jsonify({"error": "No properties provided"}), 400

        # Find the feature to update
        feature = find_feature_by_id(data["features"], feature_id)
        if feature:
            # Print the update to the server console
            print(f"Updating feature with ID {feature_id} with the following properties:")
            print(updated_properties)

            # Update the feature properties
            feature["properties"] = updated_properties

            # Save the updated data back to the JSON file
            save_json_data(data)
            return jsonify(feature), 200
        else:
            return jsonify({"error": "Feature not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a feature by ID (DELETE)
@app.route('/features/<string:feature_id>', methods=['DELETE'])
def delete_feature(feature_id):
    try:
        # Load data from JSON file
        data = load_json_data()
        feature = find_feature_by_id(data["features"], feature_id)

        if feature:
            # Remove the feature from the list
            data["features"].remove(feature)

            # Save the updated data back to the JSON file
            save_json_data(data)
            return jsonify({"message": "Feature deleted successfully"}), 200
        else:
            return jsonify({"error": "Feature not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
