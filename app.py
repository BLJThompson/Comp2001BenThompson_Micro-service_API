# app.py

from flask import render_template
from features import search_feature_by_name
import config
from config import connex_app
from models import Trail

app = config.connex_app
app.add_api(config.basedir / "swagger.yml")

@app.route("/")
def home():
    try:
        # Fetch all trails from the database
        trails = Trail.query.all()
        trails_with_features = []
        for trail in trails:
            trail_data = {
                "trail_name": trail.trail_name,
                "trail_summary": trail.trail_summary,
                "location": trail.location,
                "difficulty": trail.difficulty,
                "route_type": trail.route_type,
                "features": [tf.feature.feature_name for tf in trail.features]
            }
            trails_with_features.append(trail_data)

        return render_template("home.html", trails=trails_with_features)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)


