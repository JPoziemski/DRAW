
from bokeh.layouts import layout
from bokeh.models import Panel, Div

from visualisation import Visualisation


class ErrorPlot(Visualisation):

    def __init__(
            self,
    ):
        pass


    def get_widgets(self):
        pass

    def get_plot(self):
        """ Plot error message """
        error_message = Div(
            text="Something went wrong. \nPlease, check your data.",
            align='center',
            width=500,
            height=600,
            style={'font-size': '300%'}
        )

        return error_message

    def callback(self):
        pass

    def get_tabs(self):
        """ Get components of the plot and add them to the layout. """
        self.layout = layout([[self.get_plot()]])
        return Panel(
            child=self.layout,
            title="Error")
