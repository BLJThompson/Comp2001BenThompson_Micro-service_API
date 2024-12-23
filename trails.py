# trails.py

from models import Trail, trail_schema, trails_schema, TrailFeature, Feature, User
from flask import request, jsonify, abort
from config import db, connex_app
from marshmallow import ValidationError
from features import add_feature
from permissions import check_permission
from auth import logged_in_users


app = connex_app.app

def read_all():
    """
    Fetch all trails and their associated features, including waypoints.
    """
    # Check if the user has the required permission
    user, error = check_permission("view_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
        
    try:
        # Fetch all trails from the database
        trails = Trail.query.all()

        # Prepare a custom response that aggregates features and waypoints
        response = []
        for trail in trails:
            trail_data = trail_schema.dump(trail)
            # Add waypoint data
            trail_data["waypoints"] = {
                "pt1": {"lat": trail.pt1_lat, "long": trail.pt1_long, "desc": trail.pt1_desc},
                "pt2": {"lat": trail.pt2_lat, "long": trail.pt2_long, "desc": trail.pt2_desc},
                "pt3": {"lat": trail.pt3_lat, "long": trail.pt3_long, "desc": trail.pt3_desc},
            }
            # Remove individual waypoint fields
            for key in ["pt1_lat", "pt1_long", "pt1_desc", "pt2_lat", "pt2_long", "pt2_desc", "pt3_lat", "pt3_long", "pt3_desc"]:
                trail_data.pop(key, None)

            # Access features through TrailFeature and then through Feature
            trail_data["features"] = [
                {"feature_name": trail_feature.feature.feature_name} 
                for trail_feature in trail.features
            ]
            response.append(trail_data)

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def read_by_id(trail_id):
    """
    Retrieve a trail by its ID, restricted to users with the appropriate role.
    """
    # Check if the user has the required permission
    user, error = check_permission("view_id_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]

    try:
        # Fetch the trail by ID
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        # Prepare a custom response that aggregates features and waypoints
        trail_data = trail_schema.dump(trail)
        # Add waypoint data
        trail_data["waypoints"] = {
            "pt1": {"lat": trail.pt1_lat, "long": trail.pt1_long, "desc": trail.pt1_desc},
            "pt2": {"lat": trail.pt2_lat, "long": trail.pt2_long, "desc": trail.pt2_desc},
            "pt3": {"lat": trail.pt3_lat, "long": trail.pt3_long, "desc": trail.pt3_desc},
        }
        # Remove individual waypoint fields
        for key in ["pt1_lat", "pt1_long", "pt1_desc", "pt2_lat", "pt2_long", "pt2_desc", "pt3_lat", "pt3_long", "pt3_desc"]:
            trail_data.pop(key, None)

        # Access features through TrailFeature to Feature
        trail_data["features"] = [
            {"feature_name": trail_feature.feature.feature_name} 
            for trail_feature in trail.features
        ]

        return jsonify(trail_data), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def create_trail():
    """
    Create a trail using the logged-in user's email to link to their user ID and optionally add features and waypoints.
    Prevent duplicate features for the trail.
    """
    # Check if the user has the required permission
    user, error = check_permission("create_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]

    try:
        # Retrieve the logged-in user's email from the session
        session_id = request.cookies.get("session_id")
        if not session_id:
            return jsonify({"error": "User is not logged in."}), 401

        logged_in_user = None
        for email, user_data in logged_in_users.items():
            if user_data["session_id"] == session_id:
                logged_in_user = user_data
                break

        if not logged_in_user:
            return jsonify({"error": "Invalid session. Please log in again."}), 403

        email = logged_in_user["email"]

        # Get trail data and features from the request
        trail_data = request.json
        features = trail_data.pop("features", [])  # Extract features, if provided
        waypoints = trail_data.pop("waypoints", {})  # Extract waypoints, if provided

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

        # Deserialize and validate the trail data
        new_trail = trail_schema.load(trail_data, session=db.session)
        db.session.add(new_trail)
        db.session.commit()

        # Process the features, ensuring no duplicates
        added_features = set()  # Track added features to prevent duplicates
        for feature in features:
            feature_name = feature.get("feature_name")
            if not feature_name or feature_name in added_features:
                continue  # Skip duplicates or invalid entries
            added_features.add(feature_name)

            # Check if the feature exists
            feature_obj = Feature.query.filter_by(feature_name=feature_name).first()
            if not feature_obj:
                # If the feature does not exist, create it
                new_feature = Feature(feature_name=feature_name)
                db.session.add(new_feature)
                db.session.commit()
                feature_obj = new_feature

            # Link the feature to the trail
            trail_feature = TrailFeature(trail_id=new_trail.trail_id, feature_id=feature_obj.feature_id)
            db.session.add(trail_feature)

        # Commit the trail-feature links
        db.session.commit()

        # Return the created trail with features and waypoints
        trail_with_features = trail_schema.dump(new_trail)
        trail_with_features["features"] = [{"feature_name": feature_name} for feature_name in added_features]
        trail_with_features["waypoints"] = {
            "pt1": {"lat": trail_data["pt1_lat"], "long": trail_data["pt1_long"], "desc": trail_data["pt1_desc"]},
            "pt2": {"lat": trail_data["pt2_lat"], "long": trail_data["pt2_long"], "desc": trail_data["pt2_desc"]},
            "pt3": {"lat": trail_data["pt3_lat"], "long": trail_data["pt3_long"], "desc": trail_data["pt3_desc"],
            },
        }

        return jsonify(trail_with_features), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()  # Rollback on error
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


def update_trail(trail_id):
    """
    Update a trail's details using its ID, including waypoint updates.
    """
    # Check if the user has the required permission
    user, error = check_permission("edit_trails")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    
    
    try:
        # Get trail data from the request
        trail_data = request.json

        # Fetch the trail by ID
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        # Handle waypoint updates explicitly
        waypoints = trail_data.pop("waypoints", None)
        if waypoints:
            if "pt1" in waypoints:
                trail.pt1_lat = waypoints["pt1"].get("lat", trail.pt1_lat)
                trail.pt1_long = waypoints["pt1"].get("long", trail.pt1_long)
                trail.pt1_desc = waypoints["pt1"].get("desc", trail.pt1_desc)
            if "pt2" in waypoints:
                trail.pt2_lat = waypoints["pt2"].get("lat", trail.pt2_lat)
                trail.pt2_long = waypoints["pt2"].get("long", trail.pt2_long)
                trail.pt2_desc = waypoints["pt2"].get("desc", trail.pt2_desc)
            if "pt3" in waypoints:
                trail.pt3_lat = waypoints["pt3"].get("lat", trail.pt3_lat)
                trail.pt3_long = waypoints["pt3"].get("long", trail.pt3_long)
                trail.pt3_desc = waypoints["pt3"].get("desc", trail.pt3_desc)

        # Update other trail details
        for key, value in trail_data.items():
            if hasattr(trail, key):
                setattr(trail, key, value)

        # Commit the changes to the database
        db.session.commit()

        # Return the updated trail as a response
        return jsonify(trail_schema.dump(trail)), 200

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def delete_trail(trail_id):
    """
    Delete an existing trail by ID, including removing links to features, but keep the features intact.
    """
    # Check if the user has the required permission
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
        db.session.commit()  # Commit the deletions

        return jsonify({"message": f"Trail with ID {trail_id} and its feature links successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def add_feature_to_trail(trail_id):
    """
    Add a feature to a trail. If the feature does not exist, create it using the add_feature function.
    """
    # Check if the user has the required permission
    user, error = check_permission("add_feature_to_trail")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]   
    try:
        # Get the feature name from the request
        feature_data = request.json
        feature_name = feature_data.get("feature_name")

        # Validate input
        if not feature_name:
            return jsonify({"error": "Feature name is required."}), 400

        # Check if the trail exists
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        # Check if the feature exists
        feature = Feature.query.filter_by(feature_name=feature_name).first()
        if not feature:
            # If the feature does not exist, use the add_feature function
            feature_request_data = {"feature_name": feature_name}
            with app.test_request_context(json=feature_request_data):
                feature_response = add_feature()  # Call the add_feature function
            feature_response_data, feature_status_code = feature_response

            # Check if the feature was successfully created
            if feature_status_code != 201:
                return jsonify(feature_response_data), feature_status_code
            feature = Feature.query.filter_by(feature_name=feature_name).first()

        # Check if the feature is already linked to the trail
        existing_link = TrailFeature.query.filter_by(trail_id=trail_id, feature_id=feature.feature_id).first()
        if existing_link:
            return jsonify({"error": f"Feature '{feature_name}' is already linked to trail ID {trail_id}."}), 400

        # Link the feature to the trail
        new_link = TrailFeature(trail_id=trail_id, feature_id=feature.feature_id)
        db.session.add(new_link)
        db.session.commit()

        return jsonify({"message": f"Feature '{feature_name}' added to trail ID {trail_id}."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def remove_feature_from_trail(trail_id):
    """
    Remove a feature from a trail by deleting the association in the TrailFeature table.
    """
    # Check if the user has the required permission
    user, error = check_permission("remove_feature_from_trail")
    if error:
        return jsonify({"error": error["error"]}), error["status_code"]
    
    try:
        # Get the feature name from the request
        feature_data = request.json
        feature_name = feature_data.get("feature_name")

        # Validate input
        if not feature_name:
            return jsonify({"error": "Feature name is required."}), 400

        # Check if the trail exists
        trail = Trail.query.get(trail_id)
        if not trail:
            return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

        # Check if the feature exists
        feature = Feature.query.filter_by(feature_name=feature_name).first()
        if not feature:
            return jsonify({"error": f"Feature with name '{feature_name}' not found."}), 404

        # Check if the feature is linked to the trail
        trail_feature = TrailFeature.query.filter_by(trail_id=trail_id, feature_id=feature.feature_id).first()
        if not trail_feature:
            return jsonify({"error": f"Feature '{feature_name}' is not linked to trail ID {trail_id}."}), 400

        # Delete the association in the TrailFeature table
        db.session.delete(trail_feature)
        db.session.commit()

        return jsonify({"message": f"Feature '{feature_name}' successfully removed from trail ID {trail_id}."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
