class Visualisation:

    def prepare_data(self):
        raise NotImplementedError

    def interactive(self):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError

    def callback(self):
        raise NotImplementedError

    def get_tab(self):
        raise NotImplementedError