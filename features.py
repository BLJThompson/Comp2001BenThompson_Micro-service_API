 # feature.py
 
from flask import jsonify, request
from config import db
from models import Feature, TrailFeature, feature_schema, features_schema
from permissions import check_permission


# Read all features
def read_all_features():

    # Check if the user has the required permission
    user, error = check_permission("view_all_features")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    
    try:
        features = Feature.query.all()
        
        # Serialize the data. Transforms the list of Feature objects into a JSON-serializable format.
        result = [{"feature_id": feature.feature_id, "feature_name": feature.feature_name} for feature in features]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Search for a feature by its name and return all trails associated with it
def search_feature_by_name():

    user, error = check_permission("search_features")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    
    try:
        # Get the feature name from the query parameters
        feature_name = request.args.get('name')
        if not feature_name:
            return jsonify({"error": "Feature name is required."}), 400

        # Query the feature by name and check it exists
        feature = Feature.query.filter_by(feature_name=feature_name).first()
        if not feature:
            return jsonify({"error": f"Feature with name '{feature_name}' not found."}), 404

        # Constructs the response
        result = {
            "feature_name": feature.feature_name,
            "trails": [
                {
                    "trail_name": tf.trail.trail_name,
                    "difficulty": tf.trail.difficulty,
                    "location": tf.trail.location,
                    "length": tf.trail.length,
                    "elevation_gain": tf.trail.elevation_gain,
                    "route_type": tf.trail.route_type,
                    "trail_summary": tf.trail.trail_summary,
                    "trail_description": tf.trail.trail_description,
                    "waypoints": {
                        "pt1": {"lat": tf.trail.pt1_lat, "long": tf.trail.pt1_long, "desc": tf.trail.pt1_desc},
                        "pt2": {"lat": tf.trail.pt2_lat, "long": tf.trail.pt2_long, "desc": tf.trail.pt2_desc},
                        "pt3": {"lat": tf.trail.pt3_lat, "long": tf.trail.pt3_long, "desc": tf.trail.pt3_desc},
                        },
                    "features": [
                        {
                            "feature_name": linked_feature.feature_name
                        }
                        for linked_feature in [f.feature for f in tf.trail.features]
                    ]
                }
                for tf in feature.trails
            ]
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
     
# Add a new feature to the database.
def add_feature():

    user, error = check_permission("add_feature")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    try:
        feature_data = request.json
        feature_name = feature_data.get("feature_name")

        # Validate input
        if not feature_name:
            return {"error": "Feature name is required."}, 400

        # Check if the feature already exists
        existing_feature = Feature.query.filter_by(feature_name=feature_name).first()
        if existing_feature:
            return {"error": f"Feature '{feature_name}' already exists."}, 400

        # Create and add the new feature
        new_feature = Feature(feature_name=feature_name)
        db.session.add(new_feature)
        db.session.commit()

        return {"message": f"Feature '{feature_name}' successfully added.", "feature": {"feature_name": feature_name}}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": f"An error occurred: {str(e)}"}, 500
        
        
# Update the name of an existing feature
def update_feature_by_name(current_feature_name):

    user, error = check_permission("update_feature_by_name")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    try:
        feature_data = request.json
        new_feature_name = feature_data.get("new_feature_name")

        # Validate input
        if not new_feature_name:
            return jsonify({"error": "'new_feature_name' is required."}), 400

        # Fetch the feature by the current name
        feature = Feature.query.filter_by(feature_name=current_feature_name).first()
        if not feature:
            return jsonify({"error": f"Feature with name '{current_feature_name}' not found."}), 404

        # Check if the new feature name already exists
        existing_feature = Feature.query.filter_by(feature_name=new_feature_name).first()
        if existing_feature:
            return jsonify({"error": f"Feature with name '{new_feature_name}' already exists."}), 400

        # Update the feature name
        feature.feature_name = new_feature_name
        db.session.commit()

        return jsonify({"message": f"Feature name successfully updated from '{current_feature_name}' to '{new_feature_name}'.",
                        "feature": {"feature_name": new_feature_name}}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Delete a feature from the database
def delete_feature(feature_name):

    user, error = check_permission("delete_feature")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    
    try:
        feature = Feature.query.filter_by(feature_name=feature_name).first()

        # Check if the feature exists
        if not feature:
            return jsonify({"error": f"Feature with name '{feature_name}' not found."}), 404

        # Check if the feature is associated with any trail
        associated_trails = TrailFeature.query.filter_by(feature_id=feature.feature_id).count()
        if associated_trails > 0:
            return jsonify({"error": f"Feature '{feature_name}' is associated with one or more trails and cannot be deleted."}), 400

        # If no association exists, delete the feature
        db.session.delete(feature)
        db.session.commit()

        return jsonify({"message": f"Feature '{feature_name}' successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
