from pandas import DataFrame

class IndexCompare():
    '''
    Compares column data across all index values
    This is useful when comparing survey results, quiz scores (for specific questions)
    Best used with small pd.DF indexes
    
    Accepts a pd.DF
    
    Call IndexCompare.run() to gather the data
    
    Call self.out to print the data out to console
    '''
    def __init__(self,df: DataFrame) -> None:
        self.df = df
        self.data = {}
        
    def run(self) -> None:
        self.get_diff_df()
        self.get_comparisons()
        self._init_comparison_data()
        self.all_categories()
    
    def get_diff_df(self) -> None:
        #compare each index item accross all columns in the index
        for x in self.df.index:
            #print('X: {}'.format(x))
            self.data[x] = {}
            self.data[x]['raw'] = self.df.loc[x] - self.df.drop(x,axis=0)
            
    def get_comparisons(self) -> None:             
        #determine which index id is most similar and most different for each index
        for x in self.data:
            temp = self.data[x]['raw'].loc[self.data[x]['raw'].index != x].abs().sum(axis=1)
            self.data[x]['similar'] = {'id':temp.idxmin(),'total diff':temp.min()}
            self.data[x]['different'] = {'id':temp.idxmax(),'total diff':temp.max()}
            self.data[x]['avg total distance'] = (self.df.loc[x] - self.df.drop(x,axis=0)).abs().sum(axis=1).mean()

    def _init_comparison_data(self) -> None:    
        #init all categorization dicts
        self.most_diff = {'id':None,'total diff':None}
        self.most_same = {'id':None,'total diff':None}
        self.most_similar_to_all = {'id': None,'avg total distance': None}
        self.most_different_to_all = {'id': None, 'avg total distance': None}

    def all_categories(self) -> None:
        #find most_diff, most_same, most_similar_to_all, and most_different_to_all
        for x in self.data:
            if self.most_same['total diff'] == None or self.data[x]['similar']['total diff'] < self.most_same['total diff']:
                self.most_same['id'] = x + ' + ' + self.data[x]['similar']['id']
                self.most_same['total diff'] = self.data[x]['similar']['total diff']
                self.most_same['avg diff'] = self.most_same['total diff'] / len(self.df.columns)
            if self.most_diff['total diff'] == None or self.data[x]['different']['total diff'] > self.most_diff['total diff']:
                self.most_diff['id'] = x + ' + ' + self.data[x]['different']['id']
                self.most_diff['total diff'] = self.data[x]['different']['total diff']
                self.most_diff['avg diff'] = self.most_diff['total diff'] / len(self.df.columns)
                
            if self.most_similar_to_all['id'] == None or self.data[x]['avg total distance'] < self.most_similar_to_all['avg total distance']:
                self.most_similar_to_all['id'] = x
                self.most_similar_to_all['avg total distance'] = self.data[x]['avg total distance']
            if self.most_different_to_all['id'] == None or self.data[x]['avg total distance'] > self.most_different_to_all['avg total distance']:
                self.most_different_to_all['id'] = x
                self.most_different_to_all['avg total distance'] = self.data[x]['avg total distance']
                
            self.stats =   {'Similar':self.most_same,
                            'Different': self.most_diff,
                            'Similar to All (smallest average total distance)':self.most_similar_to_all,
                            'Different to All (largest average total distance)':self.most_different_to_all}
        
    def out(self) -> None:
        for x in self.data:
            print('{}:\nS:{},\nD:{}\n'\
                  .format(x,self.data[x]['similar'],self.data[x]['different']))
                
        for y in self.stats:
            if 'avg total distance' in self.stats[y].keys():
                print('Most {}: {}\n'\
                      'Average Total Difference: {:.2f}\n'\
                      .format(y,
                              self.stats[y]['id'],
                              self.stats[y]['avg total distance'],)
                      )
            else:
                print('Most {}: {}\n'\
                      'Total Difference: {:.2f}\n'\
                      'Average Difference: {:.2f}\n'\
                      .format(y,
                              self.stats[y]['id'],
                              self.stats[y]['total diff'],
                              self.stats[y]['avg diff'])
                      )
 