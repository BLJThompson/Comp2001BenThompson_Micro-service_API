# config.py

import pathlib
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import urllib.parse

database = "COMP2001_BThompson"
username = "BThompson"
password = "GskE483+"

encoded_password = urllib.parse.quote_plus(password)

basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.App(__name__, specification_dir=basedir)

app = connex_app.app

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mssql+pyodbc://{username}:{encoded_password}@dist-6-505.uopnet.plymouth.ac.uk/{database}?"
    "driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
