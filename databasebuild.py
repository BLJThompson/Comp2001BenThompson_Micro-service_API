from config import app, db
from models import User, Trail, Feature, TrailFeature

# Sample user data
USERS = [
    {
        "username": "Grace Hopper",
        "email": "grace@plymouth.ac.uk",
        "role": "admin"
    },
    {
        "username": "Tim Berners-Lee",
        "email": "tim@plymouth.ac.uk",
        "role": "user"
    },
    {
        "username": "Ada Lovelace",
        "email": "ada@plymouth.ac.uk",
        "role": "user"
    }
]

# Sample trail data
TRAILS = [
    {
        "trail_name": "Ocean View Trail",
        "trail_summary": "Scenic ocean view hike",
        "trail_description": "A beautiful hike along the coast.",
        "difficulty": "Easy",
        "location": "Cornwall, UK",
        "length": 5.5,
        "elevation_gain": 150,
        "route_type": "Loop",
        "user_id": 1,
        "pt1_lat": 50.1234,
        "pt1_long": -5.6789,
        "pt1_desc": "Start of the trail",
        "pt2_lat": 50.1240,
        "pt2_long": -5.6795,
        "pt2_desc": "Viewpoint overlooking the ocean",
        "pt3_lat": 50.1250,
        "pt3_long": -5.6800,
        "pt3_desc": "End of the loop"
    },
    {
        "trail_name": "Mountain Adventure Trail",
        "trail_summary": "Challenging mountain trail",
        "trail_description": "An adventurous trail through rugged mountains.",
        "difficulty": "Hard",
        "location": "Snowdonia, Wales",
        "length": 12.0,
        "elevation_gain": 850,
        "route_type": "Out-and-Back",
        "user_id": 2,
        "pt1_lat": 52.1234,
        "pt1_long": -3.6789,
        "pt1_desc": "Base of the mountain",
        "pt2_lat": 52.1240,
        "pt2_long": -3.6795,
        "pt2_desc": "Mountain peak",
        "pt3_lat": 52.1250,
        "pt3_long": -3.6800,
        "pt3_desc": "Return to base"
    }
]

# Sample feature data
FEATURES = [
    {"feature_name": "Waterfall"},
    {"feature_name": "Viewpoint"},
    {"feature_name": "Historic Landmark"}
]

# Sample trail-feature relationships
TRAIL_FEATURES = [
    {"trail_id": 1, "feature_id": 1},
    {"trail_id": 1, "feature_id": 2},
    {"trail_id": 2, "feature_id": 2},
    {"trail_id": 2, "feature_id": 3}
]

# Build the database and insert data
with app.app_context():
    db.drop_all()
    db.create_all()

    # Insert users
    print("Inserting users...")
    for user_data in USERS:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"]
        )
        db.session.add(user)

    db.session.commit()


    
    # Insert trails
    print("Inserting trails...")
    for trail_data in TRAILS:
        trail = Trail(
            trail_name=trail_data["trail_name"],
            trail_summary=trail_data["trail_summary"],
            trail_description=trail_data["trail_description"],
            difficulty=trail_data["difficulty"],
            location=trail_data["location"],
            length=trail_data["length"],
            elevation_gain=trail_data["elevation_gain"],
            route_type=trail_data["route_type"],
            user_id=trail_data["user_id"],
            pt1_lat=trail_data["pt1_lat"],
            pt1_long=trail_data["pt1_long"],
            pt1_desc=trail_data["pt1_desc"],
            pt2_lat=trail_data["pt2_lat"],
            pt2_long=trail_data["pt2_long"],
            pt2_desc=trail_data["pt2_desc"],
            pt3_lat=trail_data["pt3_lat"],
            pt3_long=trail_data["pt3_long"],
            pt3_desc=trail_data["pt3_desc"]
        )
        db.session.add(trail)

    db.session.commit()

    # Insert features
    print("Inserting features...")
    for feature_data in FEATURES:
        feature = Feature(feature_name=feature_data["feature_name"])
        db.session.add(feature)

    db.session.commit()

    # Insert trail-feature relationships
    print("Inserting trail-feature relationships...")
    for tf_data in TRAIL_FEATURES:
        trail_feature = TrailFeature(
            trail_id=tf_data["trail_id"],
            feature_id=tf_data["feature_id"]
        )
        db.session.add(trail_feature)

    db.session.commit()

    print("Database created and populated successfully!")
