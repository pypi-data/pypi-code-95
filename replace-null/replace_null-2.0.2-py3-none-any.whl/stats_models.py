import statsmodels.formula.api as smf


class StateModels:
    # Functions
    def __init__(self, data_frame=None, x=None, y=None):
        """
            Initialize class object
        """

    # Static Methods
    # --------------------------------
    @staticmethod
    def generate_summary(data_frame, x, y):
        """
        :param data_frame: Data frame
        :param x: Features Eg.x = ['TV', 'Newspaper']
        :param y: Target/Labeled value Eg.y = 'Sales'
        """
        x_data = '+'.join(x)
        if y == '' or len(x) == 0:
            return 'Something missing!!!'
        else:
            formula = f'{y} ~ {x_data}'
            linear = smf.ols(formula=formula, data=data_frame).fit()
            return linear.summary()
