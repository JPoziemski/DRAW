import pandas as pd
import numpy as np
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, HoverTool, Panel, Slider, TextInput
from bokeh.plotting import figure

from visualisation import Visualisation

class SmearPlot(Visualisation):
    """
    Plot "smear plot" showing the log2fold-change (FC, y-axis) versus the average log2 count per million
     (CPM, x-axis) of the change in gene expression.
    Slider enables selecting FDR cut-off for selecting differentially expressed genes.
    """

    def __init__(
            self,
            data: pd.DataFrame,
    ):
        self.data = data
        self.source = ColumnDataSource(self.prepare_data())
        self.layout = None
        self.cutoff = 0.05


    def prepare_data(self):
        """ Select relevant columns from the original DESeq2 results. """
        df = pd.DataFrame()
        df['log2FC'] = self.data['log2FoldChange']
        # Take log2 of CPM
        df['log2CPM'] = np.log2(self.data['baseMean'])
        df['FDR'] = self.data['padj']
        df['GeneID'] = self.data.index
        df['colors'] = 'black'
        return df

    def get_widgets(self):
        """ Create FDR cut-off slider. """

        fdr_input = TextInput(value="0.05", title="FDR cut-off (from 0 to 1):")
        fdr_input.on_change("value", self.callback)
        return [fdr_input]

    def get_plot(self):
        """ Plot scatter plot log2FC vs log2CPM. """

        hover = HoverTool(tooltips=[
            ("GeneID", "@GeneID"),
            ("log2CPM", "@log2CPM"),
            ("log2FC", "@log2FC"),
            ("FDR", '@FDR')
        ])
        # Colour the points based on a p-value cut-off
        self.source.data['colors'] = ['red' if x < self.cutoff else 'black' for x in list(self.source.data['FDR'])]
        smear_plot = figure(
            title="Smear Plot",
            plot_height=600,
            plot_width=600,
            x_axis_label='log2CPM',
            y_axis_label='log2FC',
            tools = [hover],
        )

        smear_plot.circle(
            'log2CPM',
            'log2FC',
            size=8,
            fill_color='colors',
            alpha=0.4,
            source=self.source
        )
        return smear_plot

    def callback(self, attr, old, new):
        """ Callback for FDR cut-off slider. Refresh plot each time FDR cut-off changes. """
        self.cutoff = float(new)
        self.layout.children[0].children[0] = self.get_plot()

    def get_tabs(self):
        self.layout = layout([[self.get_plot(), [widget for widget in self.get_widgets()]]])
        return Panel(
            child=self.layout,
            title="Smear Plot")