import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram
from bokeh.layouts import layout
from bokeh.models import HoverTool, Panel, Slider, TextInput, ColorBar, LinearColorMapper, ColumnDataSource, Button
from bokeh.plotting import figure
from bokeh.transform import transform
import colorcet as cc

from visualisation import Visualisation


class HeatmapPlot(Visualisation):
    """
    Heatmap of differentially expressed genes.
    Two widgets:
    :Text box enables selecting any FDR cut-off for selecting the diferentially expressed genes
    :Slider allows for selecting number of genes meeting the FDR criterium to be placed on the heatmap.

    """

    def __init__(
            self,
            count_matrix: pd.DataFrame,
            deseq_results: pd.DataFrame,
    ):
        self.count_matrix = count_matrix
        self.deseq_results = deseq_results
        self.layout = None
        self.cutoff = 1e-12
        self.n_genes_to_show = None
        self.source = None
        self.n_genes_relevant = None

    def prepare_data(self):
        """ Select relevant data from the original DESeq2 results.
         Calculate the dendogram.
         Preprare data for heatmap plotting. """

        self.deseq_results = self.deseq_results.sort_values('padj')
        relevant = list(self.deseq_results[self.deseq_results.padj < self.cutoff].index)
        df = self.count_matrix.loc[relevant, :]
        df = df.iloc[:self.n_genes_to_show]

        # Create the dendrogram
        X = pairwise_distances(df.values, metric='euclidean')
        Z = linkage(X, 'ward')
        results = dendrogram(Z, no_plot=True)
        icoord, dcoord = results['icoord'], results['dcoord']
        labels = list(map(int, results['ivl']))
        df = df.iloc[labels]

        # Reshape the data to work with Bokeh tooltips
        self.n_genes_relevant = len(df)
        genes = []
        conditions = []
        xs = []
        ys = []
        value = []
        alpha = []
        fdrs = []

        for i, gene in enumerate(df.index):
            genes = genes + [gene] * len(df.columns)
            conditions = conditions + df.columns.tolist()
            xs = xs + list(np.arange(0.5, len(df.columns) + 0.5))
            ys = ys + [i + 0.5] * len(df.columns)
            value = value + df.loc[gene].tolist()
            alpha = alpha + df.loc[gene].tolist()
            fdrs = fdrs + [self.deseq_results.loc[gene, 'padj']] * len(df.columns)

        data = pd.DataFrame(dict(
            genes=genes,
            conditions=conditions,
            xs=xs,
            ys=ys,
            value=value,
            alpha=alpha,
            fdrs=fdrs
        ))

        self.source = ColumnDataSource(data)
        return df, data, icoord, dcoord

    def calculate_n_genes_available(self):
        """ Calculate the number of genes available with a given FDR cut-off """
        self.deseq_results = self.deseq_results.sort_values('padj')
        relevant = list(self.deseq_results[self.deseq_results.padj < self.cutoff].index)
        df = self.count_matrix.loc[relevant, :]
        return len(df)

    def get_widgets(self):
        """ Create the widgets. """

        # Text box for FDR cut-off
        fdr_input = TextInput(value="1e-12", title="FDR cut-off (from 0 to 1):")
        def fdr_input_update(attr, old, new):
            """ Update FDR cutoff value.
             Update the gene slider so that the user can select only correct values. """
            self.cutoff = float(new)
            genes_to_plot.end = self.calculate_n_genes_available()

        fdr_input.on_change("value", fdr_input_update)

        genes_to_plot = Slider(
            start=2,
            end=self.n_genes_relevant,
            value=self.n_genes_relevant,
            step=1,
            title="Number of genes to plot with given FDR"
        )

        def genes_to_plot_update(attr, old, new):
            """ Update the number of genes which are to supposed to be plotted."""
            self.n_genes_to_show = int(new)

        genes_to_plot.on_change("value", genes_to_plot_update)

        run_button = Button(label="Run", button_type="success")
        run_button.on_click(self.callback)

        return [fdr_input, genes_to_plot, run_button]

    def get_plot(self):
        """Plot heatmap."""

        df, data, icoord, dcoord = self.prepare_data()

        # Define the colours
        mapper = LinearColorMapper(
            palette=cc.coolwarm,
            low=min(self.source.data['value']),
            high=max(self.source.data['value'])
        )

        # Prepare the hover tool
        hover = HoverTool()
        hover.tooltips = [
            ("Gene", "@genes"),
            ("Condition", "@conditions"),
            ("Value", "@value"),
            ("FDR", "@fdrs"),
        ]

        # Prepare the dendrogram for plotting
        icoord = pd.DataFrame(icoord)
        icoord = icoord * (data['ys'].max() / icoord.max().max())
        icoord = icoord.values
        dcoord = pd.DataFrame(dcoord)
        dcoord = dcoord * (data['xs'].max() * 0.25 / dcoord.max().max())
        dcoord = dcoord.values

        hm = figure(
            x_range=[-3, 9],
            # height=550,
            # width = 800
        )

        # Plot the dendrogram
        for i, d in zip(icoord, dcoord):
            d = list(map(lambda x: -x, d))
            hm.line(x=d, y=i, line_color='black')

        hm.add_tools(hover)

        # Plot the heatmap
        hm.rect(x='xs', y='ys',
                height=1,
                width=1,
                fill_color=transform('value', mapper),
                line_color='black',
                source=self.source,
                line_alpha=0.2,
                fill_alpha='alpha'
                )

        # Add gene names on the right side of the heatmap
        hm.text([data['xs'].max() + 0.6] * len(data['genes'].unique()),
                data['ys'].unique().tolist(),
                text=[gene for gene in data['genes']],
                text_baseline='middle',
                text_font_size='8pt',
                )

        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0)
        )

        hm.add_layout(color_bar, 'right')
        hm.axis.major_tick_line_color = None
        hm.axis.minor_tick_line_color = None
        hm.axis.major_label_text_color = None
        hm.axis.major_label_text_font_size = '0pt'
        hm.axis.axis_line_color = None
        hm.grid.grid_line_color = None
        hm.outline_line_color = None

        return hm

    def callback(self, new):
        self.layout.children[0].children[0] = self.get_plot()

    def get_tabs(self):
        self.layout = layout([[self.get_plot(), [widget for widget in self.get_widgets()]]])
        return Panel(
            child=self.layout,
            title="HeatMap")