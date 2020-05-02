import pandas as pd
import numpy as np
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, HoverTool, Panel, Slider, TextInput
from bokeh.plotting import figure

from visualisation import Visualisation

class SmearPlot(Visualisation):

    def __init__(
            self,
            data: pd.DataFrame,
    ):
        self.data = data
        self.source = ColumnDataSource(self.prepare_data())
        self.layout = None
        self.cutoff = 0.05


    def prepare_data(self):

        df = pd.DataFrame()
        df['logFC'] = self.data['log2FoldChange']
        df['logCPM'] = np.log(self.data['baseMean'])
        df['FDR'] = self.data['padj']
        df['GeneID'] = self.data.index
        df['colors'] = 'black'
        return df

    def get_widgets(self):

        fdr_input = TextInput(value="0.05", title="FDR cut-off (from 0 to 1):")
        fdr_input.on_change("value", self.callback)
        return [fdr_input]

    def get_plot(self):

        hover = HoverTool(tooltips=[
            ("GeneID", "@GeneID"),
            ("logCPM", "@logCPM"),
            ("logFC", "@logFC"),
            ("FDR", '@FDR')
        ])

        self.source.data['colors'] = ['red' if x < self.cutoff else 'black' for x in list(self.source.data['FDR'])]
        smear_plot = figure(
            title="Smear Plot",
            plot_height=600,
            plot_width=600,
            x_axis_label='logCPM',
            y_axis_label='logFC',
            tools = [hover],
        )

        smear_plot.circle(
            'logCPM',
            'logFC',
            size=8,
            fill_color='colors',
            alpha=0.4,
            source=self.source
        )
        return smear_plot

    def callback(self, attr, old, new):
        self.cutoff = float(new)
        self.layout.children[0].children[0] = self.get_plot()

    def get_tabs(self):
        self.layout = layout([[self.get_plot(), [widget for widget in self.get_widgets()]]])
        return Panel(
            child=self.layout,
            title="Smear Plot")