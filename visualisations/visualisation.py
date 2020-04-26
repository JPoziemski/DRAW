class Visualisation:

    def prepare_data(self):
        raise NotImplementedError

    def get_widgets(self):
        raise NotImplementedError

    def get_plot(self):
        raise NotImplementedError

    def callback(self):
        raise NotImplementedError

    def get_tabs(self):
        raise NotImplementedError