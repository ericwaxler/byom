import os
import json

import chart_studio.plotly as py
import plotly.graph_objs as go

from common.sqlhelper import SQLHelper
from common.repo.robinhoodrepository import robinhoodRepository

from flask import Flask, Response, jsonify, render_template

import datetime, dateutil

import io
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)


#################################################
# Database Setup
#################################################


@app.route("/")
def index():
    """Return the homepage."""
    helper = SQLHelper()
    conn = helper.getConnection()
    repo = robinhoodRepository(conn)

    return render_template("index.html")

# @app.route("/ml")
# def ml():
#     return render_template("ml.html")

# @app.route("/analysis")
# def analysis():
#     return render_template("analysis.html")

@app.route("/stocks")
def names():
    """Return stock summary information"""
    helper = SQLHelper()
    conn = helper.getConnection()
    repo = robinhoodRepository(conn)
    stockInfo = repo.getAllStocks()
    return json_response(stockInfo, 200)


# @app.route("/historic/<coin>")
# def sample_historic(coin):
#     """Return the historic data for a given sample."""
    
#     stmt = db.session.query(Prices).statement
#     df = pd.read_sql_query(stmt, db.session.bind)

#     # Filter the data based on the sample number and
#     results = df.loc[df['Currency'] == coin, ['Currency','Date','Open','High','Low','Close','Volume','MarketCap','UnixDate']]

#     results.sort_values(by='UnixDate', ascending=False, inplace=True)
#     results = results.head(100)

#     # Create a dictionary entry for each row of metadata information
#     sample_data = {
#         "Date": results.Date.values.tolist(),
#         "Open": results.Open.values.tolist(),
#         "High": results.High.values.tolist(),
#         "Low": results.Low.values.tolist(),
#         "Close": results.Close.values.tolist(),
#         "Volume": results.Volume.values.tolist(),
#         "MarketCap": results.MarketCap.values.tolist(),
#     }

#     return jsonify(sample_data)


# @app.route("/samples/<sample>")
# def samples(sample):
#     """Return `otu_ids`, `otu_labels`,and `sample_values`."""
#     stmt = db.session.query(Samples).statement
#     df = pd.read_sql_query(stmt, db.session.bind)

#     # Filter the data based on the sample number and
#     # only keep rows with values above 1
#     sample_data = df.loc[df[sample] > 1, ["otu_id", "otu_label", sample]]

#     # Sort by sample
#     sample_data.sort_values(by=sample, ascending=False, inplace=True)

#     # Format the data to send as json
#     data = {
#         "otu_ids": sample_data.otu_id.values.tolist(),
#         "sample_values": sample_data[sample].values.tolist(),
#         "otu_labels": sample_data.otu_label.tolist(),
#     }
#     return jsonify(data)

def json_response(data, code):
    return app.response_class(response=json.dumps(data, default=str), status=code, mimetype="application/json") #, use_decimal=True

if __name__ == "__main__":
    app.run()
