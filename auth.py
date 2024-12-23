from flask import request, jsonify, make_response
import requests
from models import User
from config import app, db
import uuid

# Dictionary to track logged-in users
logged_in_users = {}

AUTH_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"




@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and store their session using a custom session ID.
    """
    credentials = request.json
    response = requests.post(AUTH_URL, json=credentials)

    if response.status_code == 200:
        user_data = response.json()  # Parse the response
        email = credentials["email"]

        # Query the local database for user details
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Store the session
        logged_in_users[email] = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
            "session_id": session_id
        }

        # Set the session ID as a cookie in the response
        resp = make_response(
            jsonify({"message": "Login successful", "user": logged_in_users[email]})
        )
        resp.set_cookie("session_id", session_id, httponly=True, secure=True)

        return resp, 200

    return jsonify({"error": "Invalid credentials"}), 401








@app.route('/logout', methods=['POST'])
def logout():
    """
    Log out a user by clearing their session.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session ID."}), 400

    # Find the user by session ID
    email = None
    for logged_in_email, user_data in logged_in_users.items():
        if user_data["session_id"] == session_id:
            email = logged_in_email
            break

    if not email:
        return jsonify({"error": "No active session found."}), 404

    # Remove the user from logged_in_users
    del logged_in_users[email]

    # Clear the session ID cookie
    resp = make_response(jsonify({"message": f"User {email} logged out successfully."}))
    resp.delete_cookie("session_id")

    return resp, 200






@app.route('/auth-status', methods=['GET'])
def auth_status():
    """
    Check if a user is authenticated.
    """
    email = request.args.get("email")
    if email in logged_in_users:
        user_details = logged_in_users[email]
        return jsonify({
            "status": "authenticated",
            "user": user_details
        }), 200

    return jsonify({"status": "not authenticated"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
