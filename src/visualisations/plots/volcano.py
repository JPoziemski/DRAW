import pandas as pd
import numpy as np
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, HoverTool, Panel, Slider, TextInput
from bokeh.plotting import figure

from visualisation import Visualisation

class VolcanoPlot(Visualisation):
    """
    Plot volcano plot, showing statistical significance (P value) versus magnitude of change (fold change).
    """

    def __init__(
            self,
            data: pd.DataFrame,
    ):
        self.data = data
        self.source = ColumnDataSource(self.prepare_data())
        self.layout = None
        self.pvalue_cutoff = 0.05
        self.fc_cutoff = 0


    def prepare_data(self):
        """ Select relevant columns from the original DESeq2 results. """
        df = pd.DataFrame()
        df['log2FC'] = self.data['log2FoldChange']
        # Take log of pvalue
        df['pvalue'] = self.data['pvalue']
        df['-log10pvalue'] = -np.log(self.data['pvalue'])
        df['GeneID'] = self.data.index
        df['colors'] = 'black'
        return df

    def get_widgets(self):
        """ Create p-value cut-off slider. """

        def pvalue_callback(attr, old, new):
            """ Callback for p-value cut-off slider. Refresh plot each time p-value cut-off changes. """

            self.pvalue_cutoff = float(new)
            self.callback()

        def fc_callback(attr, old, new):
            """ Callback for FC cut-off slider. Refresh plot each time FC cut-off changes. """

            self.fc_cutoff = float(new)
            self.callback()

        pvalue_input = TextInput(value="0.05", title="P-value cut-off (from 0 to 1):")
        pvalue_input.on_change("value", pvalue_callback)

        fc_input = TextInput(value="0", title="LogFC threshold to colour")
        fc_input.on_change("value", fc_callback)



        return [pvalue_input, fc_input]

    def get_plot(self):
        """ Plot scatter plot log2FC vs -log(p-value) """

        hover = HoverTool(tooltips=[
            ("GeneID", "@GeneID"),
            ("log2FC", "@log2FC"),
            ("p-value", '@pvalue')
        ])
        # Colour the points based on a p-value cut-off and fc cut-off
        fcs = list(self.source.data['log2FC'])
        pvalues = list(self.source.data['pvalue'])
        colors = []
        labels = []
        for fc, pvalue in zip(fcs, pvalues):
            if pvalue > self.pvalue_cutoff:
                colors.append('black')
                labels.append('Not significant')
            else:
                if fc < self.fc_cutoff:
                    colors.append('#1F77B4')
                    labels.append('Down')
                else:
                    colors.append('red')
                    labels.append('Up')

        self.source.data['colors'] = colors
        self.source.data['labels'] = labels

        volcano_plot = figure(
            title="Volcano Plot",
            plot_height=600,
            plot_width=600,
            x_axis_label='log2FC',
            y_axis_label='-log10pvalue',
            tools = [hover],
        )

        volcano_plot.circle(
            'log2FC',
            '-log10pvalue',
            size=8,
            fill_color='colors',
            alpha=0.4,
            source=self.source,
            legend_group='labels'
        )

        volcano_plot.legend.orientation = "horizontal"

        return volcano_plot

    def callback(self):
        self.layout.children[0].children[0] = self.get_plot()

    def get_tabs(self):
        self.layout = layout([[self.get_plot(), [widget for widget in self.get_widgets()]]])
        return Panel(
            child=self.layout,
            title="Volcano Plot")