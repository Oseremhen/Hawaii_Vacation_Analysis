import numpy as np

import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables.
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"<h1>Welcome to the Climate App API!</h1>"
        f"<h2>Here are the routes available:</h2>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for the latest year: /api/v1.0/tobs<br/>"
        f"Temperature statistics for one day in the year(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature statistics for a range of date (start date to end date)(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    prep_selection = [Measurement.date,Measurement.prcp]
    query_result = session.query(*prep_selection).all()
    session.close()

    all_precipitation = []
    for date, prcp in query_result:
        prep_dict = {}
        prep_dict["Date"] = date
        prep_dict["Precipitation"] = prcp
        all_precipitation.append(prep_dict)

    return jsonify(all_precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stat_selection = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    query_result = session.query(*stat_selection).all()
    session.close()

    all_stations = []
    for station,name,lat,lon,el in query_result:
        stat_dict = {}
        stat_dict["Station"] = station
        stat_dict["Name"] = name
        stat_dict["Latitude"] = lat
        stat_dict["Logitude"] = lon
        stat_dict["Elevation"] = el
        all_stations.append(stat_dict)

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    query_date_year_ago = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    tobs_selection = [Measurement.date,Measurement.tobs]
    query_result = session.query(*tobs_selection).filter(Measurement.date >= query_date_year_ago).all()
    session.close()

    all_tobs = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)