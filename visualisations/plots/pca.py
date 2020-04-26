import numpy as np
import pandas as pd
import sklearn.decomposition as sk

from bokeh.layouts import row, column, layout
from bokeh.models import Select, Panel, Button, ColumnDataSource
from bokeh.palettes import Category20b_20
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

from visualisation import Visualisation


class PCAPlot(Visualisation):

    def __init__(
            self,
            data: pd.DataFrame,
    ):
        self.data = data

        self.max_pc = len(self.data.transpose())
        self.n_pcs = len(self.data.transpose())
        self.pc1 = 1
        self.pc2 = 2
        self.source = ColumnDataSource(self.prepare_data())
        self.plot = self.get_plot()
        self.layout = None

    def prepare_data(self):
        pca = sk.PCA(n_components=self.n_pcs)
        principal_components = pca.fit_transform(self.data.transpose())
        all_pc = pd.DataFrame(
            data=principal_components,
            columns=[f'principal component {i}' for i in range(1, self.n_pcs + 1)]
        )
        selected_pc = all_pc.iloc[:, [self.pc1 - 1, self.pc2 - 1]]
        # TODO - modify this line to properly substract data about experiment
        target = ['untreated' if 'untreated' in entry else 'treated' for entry in list(self.data.transpose().index)]
        color = ['black' if 'untreated' in entry else 'red' for entry in list(self.data.transpose().index)]

        pca_df = pd.concat(
            [selected_pc,
             pd.DataFrame(target, columns=['target']),
             pd.DataFrame(color, columns=['color'])],
            axis=1)
        return pca_df

    def get_widgets(self):

        pc_to_calculate = Select(
            title="Number of PC to calculate: ",
            value=str(self.max_pc),
            options=[str(i) for i in range(2, self.max_pc+1)]
        )
        pc1_to_plot = Select(
            title="Select PC to plot on x axis",
            value="1",
            options=[str(i) for i in range(1, int(pc_to_calculate.value) + 1)]
        )
        pc2_to_plot = Select(
            title="Select PC to plot on y axis",
            value="2",
            options=[str(i) for i in range(1, int(pc_to_calculate.value) + 1)]
        )

        def pc_to_calculate_update(attr, old, new):
            self.n_pcs = int(new)
            pc1_to_plot.value = "1"
            pc2_to_plot.value = "2"
            pc1_to_plot.options = [str(i) for i in range(1, int(pc_to_calculate.value)+1) if i != int(pc2_to_plot.value) ]
            pc2_to_plot.options = [str(i) for i in range(1, int(pc_to_calculate.value)+1) if i != int(pc1_to_plot.value) ]

        def pc1_to_plot_update(attr, old, new):
            self.pc1 = int(new)
            pc2_to_plot.options = [str(i) for i in range(1, int(pc_to_calculate.value) + 1) if i != int(pc1_to_plot.value) ]

        def pc2_to_plot_update(attr, old, new):
            self.pc2 = int(new)
            pc1_to_plot.options = [str(i) for i in range(1, int(pc_to_calculate.value) + 1) if i != int(pc2_to_plot.value) ]

        pc_to_calculate.on_change("value", pc_to_calculate_update)
        pc1_to_plot.on_change("value", pc1_to_plot_update)
        pc2_to_plot.on_change("value", pc2_to_plot_update)

        run_button = Button(label="Run", button_type="success")
        run_button.on_click(self.callback)

        return [pc_to_calculate, pc1_to_plot, pc2_to_plot, run_button]

    def get_plot(self):
        p = figure(
            title="Principal Component Analysis",
            plot_height=600,
            plot_width=600,

        )
        p.xaxis.axis_label = f'Principal Component {self.pc1}'
        p.yaxis.axis_label = f'Principal Component {self.pc2}'

        p.scatter(
            x=f'principal component {self.pc1}',
            y=f'principal component {self.pc2}',
            radius=0.2,
            color = 'color',
            legend_field="target",
            source=self.source,
        )

        p.legend.location = "top_left"

        return p

    def callback(self, new):
        self.source.data = self.prepare_data()
        self.layout.children[0].children[0] = self.get_plot()

    def get_tabs(self):
        self.layout = layout([[self.plot, [widget for widget in self.get_widgets()]]])
        return Panel(
            child=self.layout,
            title="PCA")
