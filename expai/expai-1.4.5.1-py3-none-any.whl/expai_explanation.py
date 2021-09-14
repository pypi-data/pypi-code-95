import plotly
from IPython.core.display import display, HTML
from expai.utils import generate_response

class ExpaiExplanation:
    """
    Class to wrap a explanation
    """
    def __init__(self, model_id: str,
                 project_id: str,
                 sample_id: str,
                 access_token: str,
                 headers: dict,
                 server_name: str,
                 raw_values,
                 session,
                 project,
                 visualizations,
                 explanation_type_id,
                 json_details):

        self.model_id = model_id
        self.project_id = project_id
        self.sample_id = sample_id

        self.server_name = server_name
        self.access_token = access_token

        self.headers = headers

        self.sess = session
        self.project = project

        self.json_details = json_details
        self.explanation_type_id = explanation_type_id
        self.visualizations = visualizations
        self.raw_values = raw_values

    def get_keys(self):
        """
        Returns the keys of every single plot available in the object.
        """
        return list(self.visualizations.keys())

    def plot(self, key: str = None):
        """
        Plot a single visualization from the object
        :param key: key of the visualization to be plotted
        """
        assert key is not None, "You must specify a key to be plotted. You can use .get_keys() to get all available keys."
        assert key in self.visualizations.keys(), "Your key doesn't exist in this explanation. You can use .get_keys() to get all available keys."

        try:
            display(HTML(plotly.io.to_html(plotly.io.from_json(str(self.visualizations[key])))))
        except:
            raise Exception("There was an error creating the plot. Please, try again.")

    def plot_all(self):
        """
        Plots all visualizations stored in the object one after the other.
        """
        def figures_to_html(figs):
            # Create unique HTML for all figures
            html = "<html><head></head><body>" + "\n"
            for fig in figs:
                inner_html = plotly.io.from_json(str(fig)).to_html().split('<body>')[1].split('</body>')[0]
                html += inner_html
            html += "</body></html>\n"
            return html

        if isinstance(self.visualizations, dict):
            html = figures_to_html(list(self.visualizations.values()))

        elif isinstance(self.visualizations, list):
            html = figures_to_html(self.visualizations)

        else:
            raise Exception("The input type for plots must be dictionary or list containing only explanations.")

        display(HTML(html))

    def get_raw_values(self):
        return self.raw_values

    def store_explanation(self,
                          explanation_name: str = None,
                          explanation_summary: str = None,
                          keys: list = None):
        """
        Store the explanation in your project for later reuse.
        :param explanation_name: Name to identify the explanation
        :param explanation_summary: Description for the plot.
        """
        assert explanation_name is not None, "You must specify a name for the explanation."

        if keys:
            assert set(keys).issubset(self.visualizations.keys()), "Some of the keys you introduce are not available. Please, try again."
        else:
            keys = self.visualizations.keys()

        data = self.json_details
        data['explanation_type_id'] = self.explanation_type_id
        data['explanation_name_des'] = explanation_name
        data['explanation_summary_des'] = explanation_summary
        data['explanation_json'] = list(self.visualizations.values())[0] #{k: v for k, v in self.visualizations.items() if k in keys}
        data['model_id'] = self.model_id
        data['sample_id'] = self.sample_id

        response = self.sess.request("POST", self.server_name + "/api/projects/{}/explanation/create".format(self.project_id),
                                    json=data, headers=self.headers)

        if response.ok:
            return "Explanation successfully created with id {}".format(response.json()['explanation_id'])
        else:
            return generate_response(response)



