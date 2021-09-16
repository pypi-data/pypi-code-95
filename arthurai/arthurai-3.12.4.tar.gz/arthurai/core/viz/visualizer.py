import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

from arthurai.common.exceptions import arthur_excepted
from arthurai.core.viz import style, utils
import warnings
warnings.filterwarnings('ignore')


class DataVisualizer(object):
    def __init__(self, arthur_model):
        self.model = arthur_model

    @arthur_excepted("failed to generate timeline")
    def timeline(self, attribute_name):
        """Generates a visualization of the distribution of an attribute over time. 
        For categorical attributes, a stacked area chart over time.
        For continuous attributes, a joyplot showing probability densities over time.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.model.get_attribute(attribute_name).categorical:
            self._timeline_categorical(self.model, attribute_name)
        else:
            self._timeline_continuous(self.model, attribute_name)

    @arthur_excepted("failed to generate metric series")
    def metric_series(self, metric_names, time_resolution="day"):
        """Generates a line series visualization for selected metrics.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(1, 1, 1)
        predicted_property, ground_truth_property = utils.get_pred_and_gt_attrs(self.model)
        pal = style.categorical_palette

        for index, metric_name in enumerate(metric_names):
            if self.model.is_batch:
                time_resolution = "batch_id"
                query = _metric_series_batch_query(metric_name, ground_truth_property, 
                    predicted_property, self.model.classifier_threshold)
            else:
                query = _metric_series_streaming_query(metric_name, time_resolution, 
                    ground_truth_property, predicted_property, self.model.classifier_threshold)

            response = self.model.query(query)
            df = pd.DataFrame(response)[::-1]

            plt.plot(df[time_resolution], df[metric_name], lw=12, color=pal[index], label=metric_name)
            plt.plot(df[time_resolution], df[metric_name], lw=2, color=pal[index])
            plt.xticks([])
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            plt.legend(loc="upper left", facecolor="white")

    @arthur_excepted("failed to generate drift series")
    def drift_series(self, attribute_names, drift_metric="PSI", time_resolution="day"):
        """Generates a line series visualization of data drift metrics for selected attributes.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(1, 1, 1)

        if self.model.is_batch:
            time_resolution = "batch_id"
        timestamp_query = _batch_timestamp_query()
        drift_query = {
            "properties": attribute_names,
            "num_bins": 20,
            "rollup": time_resolution,
            "base": {
            "source": "reference"
            },
            "target": {
            "source": "inference"
            },
            "metric": drift_metric
        }
        if self.model.is_batch:
            drift_df = pd.DataFrame(self.model.query(drift_query, query_type="drift"))
            timestamp_df = pd.DataFrame(self.model.query(timestamp_query))
            df = drift_df.rename(columns={"rollup":time_resolution}
                ).join(timestamp_df.set_index(time_resolution), on=time_resolution
                ).sort_values(by="timestamp"
                ).set_index(time_resolution)
        else:
            df = pd.DataFrame(self.model.query(drift_query, query_type="drift")
                    ).sort_values(by="rollup").set_index("rollup")

        df[attribute_names].plot(ax=ax, color=style.categorical_palette, lw=8)
        plt.ylabel(drift_metric)
        plt.xticks([])
        plt.xlabel("")
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.legend(loc="upper left", facecolor="white")

    def _timeline_categorical(self, model, attribute_name, time_resolution="day"):
        """
        """
        if self.model.is_batch:
            time_resolution="timestamp"
            query = _timeline_categorical_batch_query(attribute_name, time_resolution)
        else:
            query = _timeline_categorical_streaming_query(attribute_name, time_resolution)
        response = self.model.query(query)
        df = pd.DataFrame(response
            ).sort_values(by=time_resolution
            ).pivot(index=time_resolution,columns=attribute_name, values="count"
            ).fillna(0.0)
        
        sns.set(style="white")
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(1, 1, 1)
        plt.stackplot(df.index.values, df.values.T.tolist(), 
            labels=df.columns.values, colors=style.categorical_palette)
        plt.xticks([])
        plt.ylabel("Count")
        plt.legend(loc='upper right')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.show()



    def _timeline_continuous(self, model, attribute_name, time_resolution="day"):
        """
        """
        if self.model.is_batch:
            time_resolution="timestamp"
            query = _timeline_continuous_batch_query(attribute_name, time_resolution)
        else:
            query = _timeline_continuous_streaming_query(attribute_name, time_resolution)
        response = model.query(query)
        
        dfs= []
        for group in response:
            temp_df= pd.DataFrame(group["distribution"])
            temp_df[time_resolution] = group[time_resolution]
            temp_df["count"] = utils.savgol_filter(temp_df["count"])
            dfs.append( temp_df)
        df = pd.concat(dfs).sort_values([time_resolution, "lower"])
        
        global_y_min = df["lower"].min()
        global_y_max = df["lower"].max()
        global_x_min = df["count"].min()
        global_x_max = df["count"].max()
        
        sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
        # Initialize the FacetGrid object
        pal = style.continuous_palette
        g = sns.FacetGrid(df, col=time_resolution, hue=time_resolution, aspect=.2, height=8, palette=pal, subplot_kws={"xlim":(global_x_max, global_x_min), "ylim":(global_y_min, global_y_max)})

        # Draw the densities in a few steps
        g.map(plt.plot, "count", "lower",clip_on=False,  color="white", lw=4.5,  alpha=0.6)
        g.map(plt.fill_between, "count","lower", clip_on=False, lw=2)

        # Set the subplots to overlap
        g.fig.subplots_adjust(wspace=-.55, left = 0.125)
        g.set_titles("")
        g.set(yticks=[])
        g.set(xticks=[])
        g.set(ylabel="")
        g.set(xlabel="")
        g.despine(bottom=True, left=True)


def _metric_series_streaming_query(metric_name, time_resolution, ground_truth_property, predicted_property, classifier_threshold):
    """Generates query for fetching metrics for streaming model.
    """
    query = {
                "select": [
                    {
                        "function": metric_name,
                        "alias": metric_name,
                        "parameters": {
                            "ground_truth_property": ground_truth_property,
                            "predicted_property": predicted_property,
                            "threshold": classifier_threshold
                        }

                    },

                    {
                        "function": "roundTimestamp",
                        "alias": time_resolution,
                        "parameters": {
                            "property": "inference_timestamp",
                            "time_interval": time_resolution
                        }
                    }
                ],
                "group_by": [
                    {
                        "alias": time_resolution
                    }
                ],
                "order_by": [
                    {
                        "alias": time_resolution,
                        "direction": "desc"
                    }
                ]
            }
    return query

def _metric_series_batch_query(metric_name, ground_truth_property, predicted_property, classifier_threshold):
    """Generates query for fetching metrics for batch model.
    """
    query = {
                "select": [
                    {"function": metric_name,
                        "alias": metric_name,
                        "parameters": {
                            "ground_truth_property": ground_truth_property,
                            "predicted_property": predicted_property,
                            "threshold": classifier_threshold
                        }

                    },
                    {
                        "function":"max", 
                        "parameters": {"property":"inference_timestamp"}, 
                        "alias":"timestamp"
                    },
                    {"property":"batch_id"}
                ],
                "group_by": [
                    {
                        "property":"batch_id"
                    }
                ],
                "order_by": [
                    {
                        "alias":"timestamp",
                        "direction": "desc"
                    }
                ]
            }
    return query

def _timeline_continuous_streaming_query(attribute_name, time_resolution):
    """Generates a query for continuous attribute in a streaming model.
    """
    return {
        "select":[
            {
                "function":"distribution", 
                "alias":"distribution", 
                "parameters":{"property": attribute_name, "num_bins":50}
            },
            {
                "function": "roundTimestamp",
                "alias": time_resolution,
                "parameters": {
                    "property": "inference_timestamp",
                    "time_interval": time_resolution
                    }
            }
        ],
        "group_by": [{"alias":time_resolution} ],
        "order_by": [{"alias":time_resolution, "direction": "desc"} ]
    }

def _timeline_continuous_batch_query(attribute_name, time_resolution):
    """Generates a query for continuous attribute in a batch model.
    """
    return {
        "select":[
            {
                "function":"distribution", 
                "alias":"distribution", 
                "parameters":{"property": attribute_name, "num_bins":50}
            },
            {
                "function":"max", 
                "alias":"timestamp",
                "parameters": {"property":"inference_timestamp"}
            },
            {"property": "batch_id"}
        ],
        "group_by": [
            {
                "property":"batch_id"
            }
        ],
        "order_by": [
            {
                "alias":"timestamp",
                "direction": "desc"
            }
        ]
    }

def _timeline_categorical_streaming_query(attribute_name, time_resolution):
    """Generates a query for categorical attribute in a streaming model.
    """
    return {
        "select": [
            {
                "property": attribute_name
            },
            {
                "function": "count"
            },
            {
                "function": "roundTimestamp",
                "alias": time_resolution,
                "parameters": {
                    "property": "inference_timestamp",
                    "time_interval": time_resolution
                }
            }
        ],
        "group_by": [
            {
                "property": attribute_name
            },
            {
                "alias": time_resolution
            }
        ],
        "order_by": [
            {
                "property": attribute_name
            },
            {
                "alias": time_resolution,
                "direction": "desc"
            }
        ]
    }

def _timeline_categorical_batch_query(attribute_name, time_resolution):
    """Generates a query for categorical attribute in a batch model.
    """
    return {
        "select": [
            {
                "property": attribute_name
            },
            {
                "function": "count"
            },
            {
                "property":"batch_id"
            },
            {"function":"max", "parameters": {"property":"inference_timestamp"}, "alias":"timestamp"}
        ],
        "group_by": [
            {
                "property": attribute_name
            },
            {
                "property":"batch_id"
            }
        ],
        "order_by": [
            {
                "property": attribute_name
            },
            {
                "alias":"timestamp",
                "direction": "desc"
            }
        ]
    }

def _batch_timestamp_query():
    return {
        "select":[
            {
                "function":"max", 
                "alias":"timestamp",
                "parameters": {"property":"inference_timestamp"}
            },
            {"property": "batch_id"}
        ],
        "group_by": [
            {
                "property":"batch_id"
            }
        ],
        "order_by": [
            {
                "alias":"timestamp",
                "direction": "desc"
            }
        ]
    }