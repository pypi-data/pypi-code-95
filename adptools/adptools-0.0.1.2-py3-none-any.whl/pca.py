import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

class Reducer:
    """
    x_vars_name : array - x variables column list (e.g. - ['age', 'name', 'gender'])
    y_var_name : string - y variable name (e.g. - 'score')
    org_df : original DataFrame of x, y
    n_components : int - components number to reduce
    """
    def __init__(self, x_vars_name, y_var_name, org_df, n_components):
        self.x_vars_name = x_vars_name
        self.y_var_name = y_var_name
        self.org_df = org_df
        self.n_components = n_components

        self.pca = PCA(n_components=self.n_components)
        self.principal_df = None
        self.eigenvalue_df = None

    def reduct(self):
        x = self.org_df[self.x_vars_name]
        y = self.org_df[[self.y_var_name]]
        comp_name_list = []
        for idx in range(self.n_components):
            comp_name_list.append("PC{}".format(idx+1))
        printcipalComponents = self.pca.fit_transform(x)
        principal_df = pd.DataFrame(data=printcipalComponents, columns = comp_name_list)
        principal_df[self.y_var_name] = y
        self.principal_df = principal_df

        return self.principal_df

    def get_eigenvalue(self):
        if self.principal_df is None:
            self.principal_df = self.reduct()

        eigenvalue_list = self.pca.explained_variance_ratio_
        eigenvalue_dic = []
        for idx, eigenvalue in enumerate(eigenvalue_list):
            eigenvalue_dic.append({"comp" : "PC{}".format(idx+1), "eigenvalue" : eigenvalue})
        eigenvalue_df = pd.DataFrame(eigenvalue_dic)
        eigenvalue_df["cumsum"] = eigenvalue_df["eigenvalue"].cumsum()
        self.eigenvalue_df = eigenvalue_df

        return self.eigenvalue_df

    def scree_plot(self, figsize=(10, 10), dpi=None, vline_no=None):
        """
        figsize : scree plot figure size (e.g. (12, 12))
        dpi : scree plot figure dpi (e.g. 100)
        vline_no : if you want to draw cut-off line by elbow-point, use this parameter (e.g. 3)
        """
        if self.eigenvalue_df is None:
            self.eigenvalue_df = self.get_eigenvalue()

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(self.eigenvalue_df["comp"], self.eigenvalue_df["eigenvalue"],
                label="eigenvalue", color="orange", marker="o")
        for item in self.eigenvalue_df["eigenvalue"].items():
            plt.text(item[0], item[1], "{:4.2f}".format(item[1]), fontsize = 12,
                color="red", horizontalalignment="center", verticalalignment="bottom") 
        plt.fill_between(self.eigenvalue_df["comp"], [0 for x in range(self.n_components)],
                self.eigenvalue_df["cumsum"], color="k", alpha=0.05, label="cumsum")
        if vline_no is not None and vline_no > 0:
            plt.vlines(vline_no + 0.1, 0, 1, color="blue", linestyles="dashed")
            # plt.text(1.2, 0.8, "cumsum of var. : 0.96", fontsize = 12, color="blue")
        plt.title("Scree Plot")
        plt.xlabel("Principal Component")
        plt.ylabel("Variances")
        plt.legend()
        plt.show()

