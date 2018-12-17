 
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from datetime import timedelta
from flask import Flask, jsonify
#################################################
#DB Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement  
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date = datetime.strptime('2017-08-23', '%Y-%m-%d')
    year_ago = date - timedelta(days=365)
    # print(year_ago)
    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > year_ago).all()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    precip_data_df = pd.DataFrame(precip_data)
    precip_data_df.reindex(columns=['date'])
    # Sort the dataframe by date
    precip_data_df.sort_values(['date'])
    precip_data_dict = precip_data_df.to_dict('index')
    return jsonify(precip_data_dict)
@app.route("/api/v1.0/tobs")
def temp():
    # Choose the station with the highest number of temperature observations.
      highest_temp_count = session.query(Measurement.station, func.count(Measurement.tobs)).\
      group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).first()
      # print(highest_temp_count)
      # # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
      # Calculate the date 1 year ago from the last data point in the database
      last_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
      dates = datetime.strptime('2017-08-23', '%Y-%m-%d')
      year_ago = dates - timedelta(days=365)
      temp_data = session.query(Measurement.date, Measurement.tobs).\
      filter(Measurement.date > year_ago).filter(Measurement.station == highest_temp_count[0]).all()
      # print(temp_data)
      # Save the query results as a Pandas DataFrame
      temp_data_df = pd.DataFrame(temp_data)
      temp_data_dict = temp_data_df.to_dict('index')
      return jsonify(temp_data_dict)
      
@app.route("/api/v1.0/<start>")
def start_date(start):
    """Fetch the start date for trip for which start date matches
       the path variable supplied by the user, or a 404 if not."""

    temp_details = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    temp_details_df = pd.DataFrame(temp_details, columns=['TMIN', 'TAVG','TMAX'])
    temp_details_dict = temp_details_df.to_dict()
    return jsonify(temp_details_dict)

@app.route("/api/v1.0/<starting>/<ending>")
def start_end_date(starting,ending):
    """Fetch the start date for trip for which start date matches
       the path variable supplied by the user, or a 404 if not."""

    temp_details2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= starting).filter(Measurement.date <= ending).all()
    temp_details_df2 = pd.DataFrame(temp_details2, columns=['TMIN', 'TAVG','TMAX'])
    temp_details_dict2 = temp_details_df2.to_dict()
    return jsonify(temp_details_dict2)
if __name__ == '__main__':
    app.run(debug=True)