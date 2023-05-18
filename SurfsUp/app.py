# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurements
Stations = Base.classes.stations


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Records! These are our Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/<start>br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation values"""
    # Query all precipitations
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


if __name__ == '__main__':
    app.run(debug=True)