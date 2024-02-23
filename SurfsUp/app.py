# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from pathlib import Path
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################


app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Welcome to Phil's page<br/> <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; ***** PLEASE USE LIKE THIS /api/v1.0/2016-08-24 *****<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; *****PLEASE USE LIKE THIS /api/v1.0/2016-08-24/2016-09-05 *****<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d').date()
    year_ago = most_recent - dt.timedelta(days=365)
    precipitation_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date.between(year_ago, most_recent)).all()
    session.close()
    return jsonify(dict(precipitation_query))

@app.route("/api/v1.0/stations")
def stations():
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    return jsonify(dict(active_stations))

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d').date()
    year_ago = most_recent - dt.timedelta(days=365)
    year_temp = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').\
         order_by(Measurement.tobs).all()
    tobs= dict(year_temp)
    session.close()
    return jsonify(tobs)

def calc_start_temps(start_date):
    temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()
    return temp
        
@app.route("/api/v1.0/<start>")
def start_date(start):
    calc_start_temp = calc_start_temps(start)
    t_temp= list(np.ravel(calc_start_temp))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Average temperature': t_avg}

    return jsonify(t_dict)

def calc_temps(start_date, end_date):
    temp = session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).all()
    session.close()
    return temp


@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start, end):
    
    calc_temp = calc_temps(start, end)
    ta_temp= list(np.ravel(calc_temp))

    tmin = ta_temp[0]
    tmax = ta_temp[2]
    temp_avg = ta_temp[1]
    temp_dict = { 'Minimum temperature': tmin, 'Maximum temperature': tmax, 'Average temperature': temp_avg}

    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)