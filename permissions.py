from flask import request, jsonify
from models import User
from auth import logged_in_users

# Shared permissions
SHARED_PERMISSIONS = [
    "view_trails",
    "create_trails",
    "add_feature",
    "search_features",
    "edit_trails",
    "view_all_features",
    "add_feature_to_trail",
    "remove_feature_from_trail",
]

# Role-to-permission mappings
ROLE_PERMISSIONS = {
    "admin": SHARED_PERMISSIONS + [
        "view_id_trails",
        "edit_trails",
        "update_feature_by_name",
        "delete_feature",
        "delete_trails"
    ],
    "user": SHARED_PERMISSIONS 
}

# Retrieve the permissions associated with a given role.
def get_permissions_for_role(role):

    return ROLE_PERMISSIONS.get(role, [])

# Retrieve the currently logged-in user based on their session.
def get_user_from_request():

    session_id = request.cookies.get("session_id")
    if not session_id:
        return None, "User is not logged in."

    # Match session ID to logged-in user
    for email, user_data in logged_in_users.items():
        if user_data["session_id"] == session_id:
            return user_data, None

    return None, "User is not logged in."

# Check if the logged-in user has the required permission.
def check_permission(required_permission):

    user, error = get_user_from_request()
    if error:
        return None, {"error": error, "status_code": 401}

    # Get the user's permissions
    user_permissions = ROLE_PERMISSIONS.get(user["role"], [])
    if required_permission not in user_permissions:
        return None, {"error": "Forbidden. You do not have permission to access this resource.", "status_code": 403}

    return user, None
