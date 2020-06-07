import pandas as pd
import sklearn.decomposition as sk

from bokeh.layouts import layout
from bokeh.models import Select, Panel, Button, ColumnDataSource
from bokeh.plotting import figure

from visualisation import Visualisation


class PCAPlot(Visualisation):
    """
    Perform and plot principal component analysis (PCA).
    Two widgets (pc1_to_plot, pc2_to_plot) enable selecting which principal components should be on which axis.
    :param data: data used for plotting
    :type data: pd.DataFrame
    """

    def __init__(
            self,
            data: pd.DataFrame,
    ):
        self.data = data
        self.pca_data = None
        self.MAX_PC = len(self.data.transpose())
        self.pc1 = 1
        self.pc2 = 2
        self.source = ColumnDataSource(self.select_pca())
        self.layout = None


    def calculate_pca(self):
        """ Perform PCA. """
        pca = sk.PCA(n_components=self.MAX_PC)
        principal_components = pca.fit_transform(self.data.transpose())
        all_pc = pd.DataFrame(
            data=principal_components,
            columns=[f'principal component {i}' for i in range(1, self.MAX_PC + 1)]
        )
        return all_pc

    def select_pca(self):
        """ Choose selected principal components and  assign colors to the experimental variables. """
        if self.pca_data is None:
            self.pca_data = self.calculate_pca()
        selected_pc = self.pca_data.iloc[:, [self.pc1 - 1, self.pc2 - 1]]
        # TODO - modify this line to properly substract data about experiment
        target = ['untreated' if 'untreated' in entry else 'treated' for entry in list(self.data.transpose().index)]
        color = ['black' if 'untreated' in entry else 'red' for entry in target]

        selected_pc['target'] = target
        selected_pc['color'] = color
        return selected_pc

    def get_widgets(self):
        """ Create widgets and its callbacks for selecting PCs to plot. """
        pc1_to_plot = Select(
            title="Select PC to plot on x axis",
            value="1",
            options=[str(i) for i in range(1, int(self.MAX_PC) + 1)]
        )
        pc2_to_plot = Select(
            title="Select PC to plot on y axis",
            value="2",
            options=[str(i) for i in range(1, int(self.MAX_PC) + 1)]
        )

        def pc1_to_plot_update(attr, old, new):
            """ Update PC1 value.
            Block selecting the same value on x and y axis.
            :param attr: value to change
            :type attr: str
            :param old: old value
            :type old: float
            :param new: new value
            :type new: float
             """
            self.pc1 = int(new)
            pc2_to_plot.options = [str(i) for i in range(1, self.MAX_PC + 1) if i != int(pc1_to_plot.value)]

        def pc2_to_plot_update(attr, old, new):
            """ Update PC2 value.
            Block selecting the same value on x and y axis.
            :param attr: value to change
            :type attr: str
            :param old: old value
            :type old: float
            :param new: new value
            :type new: float
             """
            self.pc2 = int(new)
            pc1_to_plot.options = [str(i) for i in range(1, self.MAX_PC+ 1) if i != int(pc2_to_plot.value)]

        pc1_to_plot.on_change("value", pc1_to_plot_update)
        pc2_to_plot.on_change("value", pc2_to_plot_update)

        run_button = Button(label="Run", button_type="success")
        run_button.on_click(self.callback)

        return [pc1_to_plot, pc2_to_plot, run_button]

    def get_plot(self):
        """ Plot PCA. """
        pca_plot = figure(
            title="Principal Component Analysis",
            plot_height=600,
            plot_width=600,
            x_axis_label=f'Principal Component {self.pc1}',
            y_axis_label=f'Principal Component {self.pc2}',
        )

        pca_plot.scatter(
            x=f'principal component {self.pc1}',
            y=f'principal component {self.pc2}',
            radius=0.2,
            color='color',
            legend_field="target",
            source=self.source,
        )

        pca_plot.legend.location = "top_left"

        return pca_plot

    def callback(self):
        """ Update data selecting new PCs. """
        self.source.data = self.select_pca()
        self.layout.children[0].children[0] = self.get_plot()

    def get_tabs(self):
        """ Main callback. Get components of the plot and add them to the layout. """
        self.layout = layout([[self.get_plot(), [widget for widget in self.get_widgets()]]])
        return Panel(
            child=self.layout,
            title="PCA")
