# Class for replacing null values.

# filter numeric and categorical features
def filter_data_frame(df):
    data_frame = df[df.dtypes[df.dtypes != 'object'].index]
    return data_frame.isnull().sum()


class ReplaceNull:
    # Functions
    def __init__(self):
        """
            Initialize class object
        """

    # Static Methods
    # --------------------------------
    @staticmethod
    def replace_by_mean(data_frame):
        null_values = filter_data_frame(data_frame)
        # replace null value with mean
        for (item, value) in null_values.items():
            if value > 0:
                data_frame[item] = data_frame[item].fillna(
                    data_frame[item].mean())
        return data_frame

    def replace_by_mode(data_frame):
        null_values = filter_data_frame(data_frame)
        # replace null value with mean
        for (item, value) in null_values.items():
            if value > 0:
                data_frame[item] = data_frame[item].fillna(
                    data_frame[item].mode()[0])
        return data_frame

    def replace_by_median(data_frame):
        null_values = filter_data_frame(data_frame)
        # replace null value with mean
        for (item, value) in null_values.items():
            if value > 0:
                data_frame[item] = data_frame[item].fillna(
                    data_frame[item].median())
        return data_frame
