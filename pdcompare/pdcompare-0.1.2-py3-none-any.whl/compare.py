from pandas import DataFrame
from numpy import where
from warnings import warn

class Compare():
    '''
    This class compares 2 data frames. 
    It will show you what has been added,removed, and altered. 
    This will be output in a dictionary object for use.
    '''
    def __init__(self, old_df: DataFrame , new_df: DataFrame) -> None:
        '''
        old_df: what the df looked like
        new_df: what the df changed too
        '''
        self.df1 = old_df
        self.df2 = new_df

        # index check to ensure code will run properly
        self.__check_index()

        # this variable represents if we would like to compare
        # the output of the compare function
        # this currently only works with numerical (float/int)
        # values. For that reason, it defaults to False
        # but can be changed using .set_change_comparison()
        self.comparison_values = False

        # find which columns were added/removed
        # column based comparison
        # assign the following variables as lists
        self.added_cols = None
        self.removed_cols = None
        self._column_differences()
        
        # find which rows were added/removed
        # index based comparison
        self.remove = self.removed()['REMOVED']
        self.add = self.added()['ADDED']
        
        # assign cleaned versions to compare
        self.clean_df1 = self.df1.loc[~self.df1.index.isin(self.remove)].copy().sort_index()
        self.clean_df2 = self.df2.loc[~self.df2.index.isin(self.add)].copy().sort_index()

        # remove column discrepancies
        if self.removed_cols is not None:
            self.clean_df1.drop(columns=self.removed_cols,inplace=True)
        if self.added_cols is not None:
            self.clean_df2.drop(columns=self.added_cols,inplace=True)

    def __check_index(self) -> None:
        # check they are the same type
        if self.df1.index.dtype != self.df2.index.dtype:
            raise ValueError("Your indexes are not the same type. "\
                            "Please re-initalize the class with 2 DataFrames "\
                            "that have the same index")
        
        # check they are the same name (only a warning)
        if self.df1.index.name != self.df2.index.name:
            warn("Your indexes are not the same name, please ensure "\
                    "they are the same unique identifier. "\
                    "You may experience strange output",
                    category=RuntimeWarning,
                    stacklevel=2
                )

    def _column_differences(self) -> None:
        self.added_cols = [x for x in self.df2.columns if x not in self.df1.columns]
        self.removed_cols = [x for x in self.df1.columns if x not in self.df2.columns]

    def set_change_comparison(self, change_value: bool) -> None:
        self.comparison_values = change_value

    def compare(self) -> DataFrame:
        '''
        COMPARE 2 pd.dfs and returns the index & columns as well as what changed.
        
        Indexes must be matching same length/type
        
        Based on
        https://stackoverflow.com/questions/17095101/
        compare-two-dataframes-and-output-their-differences-side-by-side
        '''
        try:
            ne_stacked = (self.clean_df1 != self.clean_df2).stack()
            changed = ne_stacked[ne_stacked]
            changed.index.names = ['ID', 'Column']
            difference_locations = where(self.clean_df1 != self.clean_df2)

        except ValueError:
            raise ValueError("Please make sure your Indexes are named the same, and the same type")
        
        changed_from = self.clean_df1.values[difference_locations]
        changed_to = self.clean_df2.values[difference_locations]
        
        final = DataFrame({'from': changed_from, 'to': changed_to},index=changed.index)
        final.dropna(how='all',inplace=True)

        if self.comparison_values:
            final['change'] = final['to'] - final['from']

        self.change_detail = final
        
        return self.summary()
    
    def removed(self,full: bool = False) -> DataFrame:
        '''
        full: bool: if True will return the entire row, if False just the index
        '''
        if full:
            return self.df1.loc[~self.df1.index.isin(self.df2.index)]
        else:
            return DataFrame(self.df1.loc[~self.df1.index.isin(self.df2.index)].index.values, columns = ['REMOVED'])
    
    def added(self,full: bool = False) -> DataFrame:
        '''
        full: bool: if True will return the entire row, if False just the index
        '''
        if full:
            return self.df2.loc[~self.df2.index.isin(self.df1.index)]
        else:
            return DataFrame(self.df2.loc[~self.df2.index.isin(self.df1.index)].index.values, columns = ['ADDED'])
    
    def output(self) -> dict:
        output_dict =  {'SUMMARY': self.summary(),
                        'ADDED': self.add,
                        'ADDED_cols': self.added_cols,
                        'REMOVED': self.remove,
                        'REMOVED_cols': self.removed_cols,
                        'CHANGED':self.change_detail,
                        }
        return output_dict
    
    def summary(self) -> DataFrame:
        summary_dict  = {
                        'Total Rows in Old': [self.df1.shape[0]],
                        'Total Rows in New': [self.df2.shape[0]],
                        'Rows Added': [self.add.shape[0]],
                        'Rows Removed': [self.remove.shape[0]],
                        "Columns Added": [len(self.added_cols)],
                        "Columns Removed": [len(self.removed_cols)],
                        'Total Changes': [self.change_detail.shape[0]]
                        }

        return DataFrame.from_dict(summary_dict)
