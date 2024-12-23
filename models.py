import pytz
from config import db, ma
from marshmallow.fields import Method, Integer
from marshmallow_sqlalchemy import fields


# User Model
class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'schema': 'CW2'}

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)

    # Define relationship
    trails = db.relationship(
        'Trail',
        backref='owner',
        cascade="all, delete, delete-orphan",
        single_parent=True,
        lazy='joined'  # Eagerly load trails to avoid lazy-loading overhead
    )

# Trail Model
class Trail(db.Model):
    __tablename__ = "trails"
    __table_args__ = {'schema': 'CW2'}

    trail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trail_name = db.Column(db.String(100), nullable=False, unique=True)
    trail_summary = db.Column(db.String(255), default="No summary provided.")
    trail_description = db.Column(db.String(255), default="No description provided.")
    difficulty = db.Column(db.String(50), default="Unknown")
    location = db.Column(db.String(150), default="Unknown")
    length = db.Column(db.Float, default=0.0)
    elevation_gain = db.Column(db.Float, default=0.0)
    route_type = db.Column(db.String(50), default="Unknown")
    user_id = db.Column(db.Integer, db.ForeignKey("CW2.users.user_id"), nullable=False)
    
    # Waypoints
    pt1_lat = db.Column(db.Float, nullable=True)
    pt1_long = db.Column(db.Float, nullable=True)
    pt1_desc = db.Column(db.String(255), nullable=True)

    pt2_lat = db.Column(db.Float, nullable=True)
    pt2_long = db.Column(db.Float, nullable=True)
    pt2_desc = db.Column(db.String(255), nullable=True)

    pt3_lat = db.Column(db.Float, nullable=True)
    pt3_long = db.Column(db.Float, nullable=True)
    pt3_desc = db.Column(db.String(255), nullable=True)

    # Relationship to TrailFeature
    features = db.relationship(
        'TrailFeature',
        back_populates='trail',
        lazy=True
    )

# Feature Model
class Feature(db.Model):
    __tablename__ = "features"
    __table_args__ = {'schema': 'CW2'}

    feature_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feature_name = db.Column(db.String(100), nullable=False, unique=True)

    # Relationship to TrailFeature
    trails = db.relationship(
        'TrailFeature',
        back_populates='feature',
        lazy=True
    )

# Link Table Model
class TrailFeature(db.Model):
    __tablename__ = "trail_features"
    __table_args__ = {'schema': 'CW2'}

    trail_id = db.Column(db.Integer, db.ForeignKey("CW2.trails.trail_id"), primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey("CW2.features.feature_id"), primary_key=True)

    # Define relationships
    trail = db.relationship('Trail', back_populates='features')
    feature = db.relationship('Feature', back_populates='trails')

# User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships = True

    # Avoid circular references
    trails = fields.Nested("TrailSchema", exclude=("owner",), many=True)

# Trail Schema
class TrailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Trail
        load_instance = True

    waypoints = Method("get_waypoints")

    def get_waypoints(self, obj):
        return {
            "pt1": {"lat": obj.pt1_lat, "long": obj.pt1_long, "desc": obj.pt1_desc},
            "pt2": {"lat": obj.pt2_lat, "long": obj.pt2_long, "desc": obj.pt2_desc},
            "pt3": {"lat": obj.pt3_lat, "long": obj.pt3_long, "desc": obj.pt3_desc},
        }

    # Explicitly include user_id
    user_id = Integer(required=True)

    # Avoid circular references
    owner = fields.Nested("UserSchema", exclude=("trails",))
    features = fields.Nested("TrailFeatureSchema", many=True)

# Feature Schema
class FeatureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feature
        load_instance = True

    trails = fields.Nested("TrailFeatureSchema", many=True)

# TrailFeature Schema
class TrailFeatureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrailFeature
        load_instance = True

    trail = fields.Nested("TrailSchema", exclude=("features",))
    feature = fields.Nested("FeatureSchema", exclude=("trails",))

# Create schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
trail_schema = TrailSchema()
trails_schema = TrailSchema(many=True)
feature_schema = FeatureSchema()
features_schema = FeatureSchema(many=True)
trail_feature_schema = TrailFeatureSchema()
trail_features_schema = TrailFeatureSchema(many=True)
