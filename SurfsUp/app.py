# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#KD- I will be initiating a session under each API, otherwise I was getting error executing this code

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Initiate a session
    session = Session(engine)

    #Create empty dictionary for storing precipitation values
    precipitation = []

    ### Retrieve the last 12 months of precipitation data ###
    # Calculate the date one year from the last date in data set.
    earliest_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    # Create the list of parameters
    data = [Measurement.date, func.round(Measurement.prcp, 2)]

    # Run the query with created parameters and additional filters
    prcp_data = session.query(*data).filter(func.strftime(Measurement.date) >= earliest_date).all()
    
    #End the session
    session.close()

    #Add data into a dictionary:
    for date, prcp in prcp_data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation.append(precipitation_dict)

    # return JSON formatted data
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    #Initiate a session
    session = Session(engine)

    #Create empty dictionary for storing station values
    stations = []

    """Return a JSON list of stations from the dataset."""
    # Create the list of parameters for the query
    station_data = [Station.id, 
                    Station.station, 
                    Station.name, 
                    Station.latitude, 
                    Station.longitude, 
                    Station.elevation]
    
    # Run the query with created parameters
    results = session.query(*station_data).all()

    #End the session
    session.close()

    # Re-write query results into a dictionary:
    for id, station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        stations.append(station_dict)

    # return JSON formatted data
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #Initiate a session
    session = Session(engine)

    #Create empty dictionary for storing station values
    tobs_json = []

    # Query the dates and temperature observations of the most-active station for the previous year of data
    # Create the list of parameters for the query
    tobs_data = [Measurement.date, 
                 Measurement.tobs]
    
    # Define the ealiest_date variable
    earliest_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Run the query with created parameters and additional filters
    results = session.query(*tobs_data).filter((func.strftime(Measurement.date) >= earliest_date),(Measurement.station == 'USC00519281')).all()

    #End the session
    session.close()

    # Re-write query results into a dictionary
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs
        tobs_json.append(tobs_dict)

    # return JSON formatted data
    return jsonify(tobs_json)

if __name__ == '__main__':
    app.run(debug=True)
