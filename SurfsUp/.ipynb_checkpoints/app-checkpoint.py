#################################################
# Importing dependencies.
#################################################
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting an existing database into a new model
Base = automap_base()

# Reflecting the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br>"
        f"Note: Please replace 'start_date' and 'end_date' with your desired dates in the following format: 'YYYY-MM-DD'"
)



#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation values for the past year"""
    
    # Query all precipitations
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()

    # Closing session
    session.close()

    # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


#################################################
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    # Closing session
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        all_stations.append(stations_dict)

    return jsonify(all_stations)


#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of all temperature values from the most active station"""
    
    # Query all tobs from the past year, from the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').all()
    
    # Closing session
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)


#################################################
@app.route("/api/v1.0/<start_date>")
def temps_start(start_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature
    for a period given the start date"""
    
    print(f"Climate app summary values are requested from {start_date}...")

    # Defining a new function to calculate the values from a particular start date 
    # (datetime object in the format "%Y-%m-%d")
    def sum_values(start_date):
        """"Return a list of Min, Max and Avr values from the selected date on"""

        sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        return session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d", start_date)).group_by(Measurement.date).all()

        # Closing session
        session.close()

    try:
        # Converting the start date to a datetime object for validating and error handling
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")

        # Calling the function to calculate the values from the start date and saving the result
        results = sum_values(start_date)
        all_values =[]

        # For loop to go through row and calculate values
        for start_date, tmin, tavg, tmax in results:
            temps_dict = {}
            temps_dict["date"] = start_date
            temps_dict["tmin"] = tmin
            temps_dict["tavg"] = tavg
            temps_dict["tmax"] = tmax
            all_values.append(temps_dict)

        return jsonify(all_values)

    except ValueError:
        return "Please enter a start date in the format 'YYYY-MM-DD'"
    
    
    
#################################################
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_period(start_date, end_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature
    for a period given the start and end dates"""
    
    print(f"Climate app summary values are requested from {start_date} to {end_date}...")

    # Defining a new function to calculate the values from a particular start-end date 
    # (datetime object in the format "%Y-%m-%d")
    def sum_values(start_date, end_date):
        """"Return a list of Min, Max and Avr values for the selected period"""

        sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        return session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d", start_date)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= func.strftime("%Y-%m-%d", end_date)).group_by(Measurement.date).all()

        # Closing session
        session.close()

    try:
        # Converting the dates to a datetime object for validating and error handling
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
        
        # Calling the function to calculate the values from the start-end dates and saving the result
        results = sum_values(start_date, end_date)
        all_values_period =[]

        # For loop to go through rows and calculate values
        for temp_date, tmin, tavg, tmax in results:
            temps_dict = {}
            temps_dict["date"] = temp_date
            temps_dict["tmin"] = tmin
            temps_dict["tavg"] = tavg
            temps_dict["tmax"] = tmax
            all_values_period.append(temps_dict)

        return jsonify(all_values_period)

    except ValueError:
        return "Please enter the desired dates in the format 'YYYY-MM-DD'"

    
if __name__ == "__main__":
    app.run(debug=True)