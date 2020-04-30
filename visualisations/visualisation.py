import abc


class Visualisation:

    @abc.abstractmethod
    def prepare_data(self):
        return

    @abc.abstractmethod
    def get_widgets(self):
        return

    @abc.abstractmethod
    def get_plot(self):
        return

    @abc.abstractmethod
    def callback(self):
        return

    @abc.abstractmethod
    def get_tabs(self):
        return