from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.models.widgets import Tabs
from bokeh.themes import Theme

from flask import Flask, render_template
import webbrowser
import pandas as pd
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

import sys
sys.path.insert(1, '../src/visualisations/')

import argparse
from plots.pca import PCAPlot
from plots.smear import SmearPlot
from plots.volcano import VolcanoPlot
from plots.heatmap import HeatmapPlot

app = Flask(__name__)
port = 5000

def parse_arguments():
    """Get id and data type for visualisation. """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-id', help='ID of the run')
    parser.add_argument('-dt', choices=['vsd', 'rld', 'norm'], default='vsd',
                        help='Main type of data to use in the visualisation')
    args = parser.parse_args()
    return args.id, args.dt

def get_plot(doc):
    """Get the plots and set up the layout.
    :param doc: document we will output.
    :type doc: Document
    """
    id_run, data_type = parse_arguments()

    data = pd.read_csv(f'../src/visualisations/data/{data_type}.csv', index_col=0)
    res = pd.read_csv(f'../src/visualisations/data/res.csv', index_col=0)
    smear_plot = SmearPlot(res)
    tab1 = smear_plot.get_tabs()

    pca_plot = PCAPlot(data)
    tab2 = pca_plot.get_tabs()

    volcano_plot = VolcanoPlot(res)
    tab3 = volcano_plot.get_tabs()

    heatmap_plot = HeatmapPlot(
        count_matrix=data,
        deseq_results=res,

    )
    tab4 = heatmap_plot.get_tabs()

    doc.theme = Theme('../src/visualisations/theme.yaml')
    doc.add_root(Tabs(tabs=[tab1, tab2, tab3, tab4]))
    doc.title = "DRAW report"


bokeh_app = Application(FunctionHandler(get_plot))

@app.route('/', methods = ['GET'])
def index():
    """ Generate a script to load the session and use the script in the rendered page. """
    script = server_document('http://localhost:5001/bkapp')
    return render_template("index.html", script = script)

def bk_worker():
    """ Run Bokeh server. """
    server = Server(
        {'/bkapp': bokeh_app},
        io_loop = IOLoop(),
        allow_websocket_origin = ["localhost:{}".format(port)], port = port
    )
    server.start()
    server.io_loop.start()

from threading import Thread
Thread(target = bk_worker).start()

if __name__ == '__main__':
    print('Opening single process Flask app with embedded Bokeh application on http://localhost:{}/'.format(port))
    webbrowser.open_new("http://localhost:{}/".format(port))
    app.run(port = port, debug = False)