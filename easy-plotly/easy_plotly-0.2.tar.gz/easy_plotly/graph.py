import plotly.graph_objects as go

class Graph:
    """
    General Graph class for making visualizations easily
    """

    def __init__(self):
        self.fig = go.Figure()

    def show_chart(self):
        """
        Method that exports the chart
        """
        self.fig.show()

    def update_layout(self, title, x_title="", y_title="", x_suffix="", y_suffix="", paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)'):
        """
        Updates layout

        Attributes:
            title (string): Title of the chart
            x_title (string): X-axis label
            y_title (string): Y-axis label
            x_suffix (string): X-axis suffix, e.g. %
            y_suffix (string): Y-axis suffix, e.g. %
            paper_bgcolor (string): Sets the color of paper where the graph is drawn, e.g. "white"
            plot_bgcolor (string): Sets the background color of plotly area, e.g. "white"
        """
        self.title = title
        self.x_suffix = x_suffix
        self.y_suffix = y_suffix
        self.paper_bgcolor = paper_bgcolor
        self.plot_bgcolor = plot_bgcolor

        self.fig.update_layout(
            title={'text': self.title},
            yaxis=dict(ticksuffix=self.y_suffix, title=y_title),
            xaxis=dict(ticksuffix=self.x_suffix, title=x_title),
            paper_bgcolor=self.paper_bgcolor,
            plot_bgcolor=self.plot_bgcolor)



