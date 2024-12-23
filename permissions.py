from flask import request, jsonify
from models import User
from auth import logged_in_users

# Shared permissions
SHARED_PERMISSIONS = [
    "view_trails",
    "create_trails",
    "add_feature",
    "search_features",
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

def get_permissions_for_role(role):
    """
    Retrieve the permissions associated with a given role.
    """
    return ROLE_PERMISSIONS.get(role, [])

def get_user_from_request():
    """
    Retrieve the currently logged-in user based on their session.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None, "User is not logged in."

    # Match session ID to logged-in user
    for email, user_data in logged_in_users.items():
        if user_data["session_id"] == session_id:
            return user_data, None

    return None, "User is not logged in."

def role_required(required_permissions):
    """
    Decorator to enforce role-based access control.
    """
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get the user from the request
            user, error = get_user_from_request()
            if error:
                return jsonify({"error": error}), 401

            # Check user permissions
            user_permissions = get_permissions_for_role(user.role)
            if not any(perm in user_permissions for perm in required_permissions):
                return jsonify({"error": "Forbidden. Insufficient permissions."}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator

def check_permission(required_permission):
    """
    Check if the logged-in user has the required permission.
    """
    user, error = get_user_from_request()
    if error:
        return None, {"error": error, "status_code": 401}

    # Get the user's permissions
    user_permissions = ROLE_PERMISSIONS.get(user["role"], [])
    if required_permission not in user_permissions:
        return None, {"error": "Forbidden. You do not have permission to access this resource.", "status_code": 403}

    return user, None
