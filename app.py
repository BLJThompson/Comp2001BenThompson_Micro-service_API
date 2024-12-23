# app.py

from flask import render_template
from features import search_feature_by_name  # Import the features Blueprint
import config
from config import connex_app  # Import connex_app
from models import Trail

app = config.connex_app
app.add_api(config.basedir / "swagger.yml")

@app.route("/")
def home():
    """
    Render the homepage with all trails.
    """
    try:
        # Fetch all trails from the database
        trails = Trail.query.all()

        # Render the template and pass the trails
        return render_template("home.html", trails=trails)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)


