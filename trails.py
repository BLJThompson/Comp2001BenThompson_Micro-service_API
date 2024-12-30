# trails.py

from models import Trail, trail_schema, trails_schema, TrailFeature, Feature, User
from flask import request, jsonify, abort
from config import db, connex_app
from marshmallow import ValidationError
from features import add_feature
from permissions import check_permission
from auth import logged_in_users


app = connex_app.app

# Fetch all trails and their associated features, including waypoints.
def read_all():
        
    try:
        # Fetch all trails from the database
        trails = Trail.query.all()

        # Iterate through each trail and merges the way the waypoints and features are displayed
        response = []
        for trail in trails:
            trail_data = trail_schema.dump(trail)
            # Groups the individual waypoint attributes (pt1_lat, pt1_long, etc.) into nested dictionaries.
            trail_data["waypoints"] = {
                "pt1": {"lat": trail.pt1_lat, "long": trail.pt1_long, "desc": trail.pt1_desc},
                "pt2": {"lat": trail.pt2_lat, "long": trail.pt2_long, "desc": trail.pt2_desc},
                "pt3": {"lat": trail.pt3_lat, "long": trail.pt3_long, "desc": trail.pt3_desc},
            }
            # Removes the original individual waypoint fields (pt1_lat, pt2_long, etc.) from the trail data.
            for key in ["pt1_lat", "pt1_long", "pt1_desc", "pt2_lat", "pt2_long", "pt2_desc", "pt3_lat", "pt3_long", "pt3_desc"]:
                trail_data.pop(key, None)

            # Add Features to Trail Data
            trail_data["features"] = [
                {"feature_name": trail_feature.feature.feature_name} 
                for trail_feature in trail.features
            ]
            response.append(trail_data)

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Retrieve a trail by its ID, restricted to users with the appropriate role.
def read_by_id(trail_id):

    # Check if the user has the required permission
    user, error = check_permission("view_id_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]

    try:
        # Fetch the trail by ID
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        # Merges the way the waypoints and features are displayed
        trail_data = trail_schema.dump(trail)
        trail_data["waypoints"] = {
            "pt1": {"lat": trail.pt1_lat, "long": trail.pt1_long, "desc": trail.pt1_desc},
            "pt2": {"lat": trail.pt2_lat, "long": trail.pt2_long, "desc": trail.pt2_desc},
            "pt3": {"lat": trail.pt3_lat, "long": trail.pt3_long, "desc": trail.pt3_desc},
        }
        # Removes the original individual waypoint fields (pt1_lat, pt2_long, etc.) from the trail data.
        for key in ["pt1_lat", "pt1_long", "pt1_desc", "pt2_lat", "pt2_long", "pt2_desc", "pt3_lat", "pt3_long", "pt3_desc"]:
            trail_data.pop(key, None)

        # Add Features to Trail Data
        trail_data["features"] = [
            {"feature_name": trail_feature.feature.feature_name} 
            for trail_feature in trail.features
        ]

        return jsonify(trail_data), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Create a trail using the logged-in user's email to link to their user ID
def create_trail():

    user, error = check_permission("create_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]

    try:
        # Retrieve the logged-in user's email from the session cookies
        session_id = request.cookies.get("session_id")
        if not session_id:
            return jsonify({"error": "User is not logged in."}), 401

        # Matches the session_id to a logged-in user in logged_in_users and returns error
        logged_in_user = None
        for email, user_data in logged_in_users.items():
            if user_data["session_id"] == session_id:
                logged_in_user = user_data
                break

        if not logged_in_user:
            return jsonify({"error": "Invalid session. Please log in again."}), 403
        email = logged_in_user["email"]

        # Extracts trail details, features, and waypoints from the request body.
        trail_data = request.json
        features = trail_data.pop("features", [])
        waypoints = trail_data.pop("waypoints", {})

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": f"No user found with email {email}"}), 404

        # Add user_id to trail_data
        trail_data["user_id"] = user.user_id

        # Process waypoints
        trail_data["pt1_lat"] = waypoints.get("pt1", {}).get("lat")
        trail_data["pt1_long"] = waypoints.get("pt1", {}).get("long")
        trail_data["pt1_desc"] = waypoints.get("pt1", {}).get("desc")
        trail_data["pt2_lat"] = waypoints.get("pt2", {}).get("lat")
        trail_data["pt2_long"] = waypoints.get("pt2", {}).get("long")
        trail_data["pt2_desc"] = waypoints.get("pt2", {}).get("desc")
        trail_data["pt3_lat"] = waypoints.get("pt3", {}).get("lat")
        trail_data["pt3_long"] = waypoints.get("pt3", {}).get("long")
        trail_data["pt3_desc"] = waypoints.get("pt3", {}).get("desc")

        # Deserialize and converts the trail_data dictionary into a Trail model object.
        new_trail = trail_schema.load(trail_data, session=db.session)
        db.session.add(new_trail)
        db.session.commit()

        # Add features to the trail and avoid duplicates
        added_features = set()
        for feature in features:
            feature_name = feature["feature_name"]
            if feature_name in added_features:
                continue
            added_features.add(feature_name)

            # Check if the feature exists in the database
            existing_feature = Feature.query.filter_by(feature_name=feature_name).first()
            if not existing_feature:
                # Create the feature if it doesn't exist
                new_feature = Feature(feature_name=feature_name)
                db.session.add(new_feature)
                db.session.commit()
                existing_feature = new_feature

            # Link the feature to the trail
            trail_feature = TrailFeature(trail_id=new_trail.trail_id, feature_id=existing_feature.feature_id)
            db.session.add(trail_feature)

        # Commit the trail-feature links
        db.session.commit()

        # Converts object into dictionary to formant response
        trail_with_features = trail_schema.dump(new_trail)
        trail_with_features["features"] = [
            {"feature_name": tf.feature.feature_name} for tf in new_trail.features
        ]
        trail_with_features["waypoints"] = {
            "pt1": {"lat": trail_data["pt1_lat"], "long": trail_data["pt1_long"], "desc": trail_data["pt1_desc"]},
            "pt2": {"lat": trail_data["pt2_lat"], "long": trail_data["pt2_long"], "desc": trail_data["pt2_desc"]},
            "pt3": {"lat": trail_data["pt3_lat"], "long": trail_data["pt3_long"], "desc": trail_data["pt3_desc"]}
        }

        return jsonify(trail_with_features), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Update a trail's details using its ID
def update_trail(trail_id):

    user, error = check_permission("edit_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]

    try:
        # Fetch the trail by ID from the input parameter 
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        trail_data = request.json

        # Validates trail name
        new_name = trail_data.get("trail_name")
        if new_name and new_name != trail.trail_name:
            existing_trail = Trail.query.filter_by(trail_name=new_name).first()
            if existing_trail:
                return jsonify({"error": f"A trail with the name '{new_name}' already exists."}), 400

        # Update trail details
        for key, value in trail_data.items():
            if key not in ["features", "waypoints"] and hasattr(trail, key):
                setattr(trail, key, value)

        # Update waypoints
        waypoints = trail_data.pop("waypoints", None)
        if waypoints:
            trail.pt1_lat = waypoints.get("pt1", {}).get("lat", trail.pt1_lat)
            trail.pt1_long = waypoints.get("pt1", {}).get("long", trail.pt1_long)
            trail.pt1_desc = waypoints.get("pt1", {}).get("desc", trail.pt1_desc)

            trail.pt2_lat = waypoints.get("pt2", {}).get("lat", trail.pt2_lat)
            trail.pt2_long = waypoints.get("pt2", {}).get("long", trail.pt2_long)
            trail.pt2_desc = waypoints.get("pt2", {}).get("desc", trail.pt2_desc)

            trail.pt3_lat = waypoints.get("pt3", {}).get("lat", trail.pt3_lat)
            trail.pt3_long = waypoints.get("pt3", {}).get("long", trail.pt3_long)
            trail.pt3_desc = waypoints.get("pt3", {}).get("desc", trail.pt3_desc)

        # Handle feature updates
        features = trail_data.pop("features", None)
        if features:
            # Add new features
            if "add" in features:
                feature_request_data = {"feature_name": features["add"]}
                with app.test_request_context(json=feature_request_data):
                    add_feature_to_trail(trail_id)

            # Remove features
            if "remove" in features:
                feature_request_data = {"feature_name": features["remove"]}
                with app.test_request_context(json=feature_request_data):
                    remove_feature_from_trail(trail_id)

        # Commit changes
        db.session.commit()

        # Api trail response
        updated_trail = trail_schema.dump(trail)
        updated_trail["features"] = [
            {"feature_name": tf.feature.feature_name} for tf in trail.features
        ]

        return jsonify(updated_trail), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Delete an existing trail by ID, including removing links to features
def delete_trail(trail_id):

    user, error = check_permission("delete_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]    
    
    try:
        # Fetch the trail to delete
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        # Delete all links to features in the TrailFeature table
        TrailFeature.query.filter_by(trail_id=trail_id).delete(synchronize_session=False)

        # Delete the trail itself
        db.session.delete(trail)
        db.session.commit()

        return jsonify({"message": f"Trail with ID {trail_id} and its feature links successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Add features to a trail
def add_feature_to_trail(trail_id):

    try:
        # Get the feature name(s) from the request
        feature_data = request.json
        feature_names = feature_data.get("feature_name")

        # Ensure feature_names is a list for consistency incase only 1 is added
        if isinstance(feature_names, str):
            feature_names = [feature_names]
        if not feature_names:
            return jsonify({"error": "Feature name or list of feature names is required."}), 400


        # Iterate through feature names and link them
        for feature_name in feature_names:
            # Check if the feature exists
            feature = Feature.query.filter_by(feature_name=feature_name).first()
            if not feature:
                # Create the feature if it doesn't exist
                feature = Feature(feature_name=feature_name)
                db.session.add(feature)
                db.session.commit()

            # Check if the feature is already linked to the trail
            existing_link = TrailFeature.query.filter_by(trail_id=trail_id, feature_id=feature.feature_id).first()
            if existing_link:
                continue

            # Link the feature to the trail
            new_link = TrailFeature(trail_id=trail_id, feature_id=feature.feature_id)
            db.session.add(new_link)

        # Commit all changes
        db.session.commit()

        return jsonify({"message": f"Features successfully added to trail ID {trail_id}."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Remove features from a trail
def remove_feature_from_trail(trail_id):

    try:
        # Get the feature name(s) from the request
        feature_data = request.json
        feature_names = feature_data.get("feature_name")

        if not feature_names:
            return jsonify({"error": "Feature name or list of feature names is required."}), 400

        # Ensure feature_names is a list for consistency incase only 1 is added
        if isinstance(feature_names, str):
            feature_names = [feature_names]

        # Iterate through feature names and unlink them
        for feature_name in feature_names:
            # Check if the feature exists
            feature = Feature.query.filter_by(feature_name=feature_name).first()
            if not feature:
                continue

            # Check if the feature is linked to the trail
            trail_feature = TrailFeature.query.filter_by(trail_id=trail_id, feature_id=feature.feature_id).first()
            if trail_feature:
                db.session.delete(trail_feature)

        # Commit changes
        db.session.commit()

        return jsonify({"message": f"Features successfully removed from trail ID {trail_id}."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
