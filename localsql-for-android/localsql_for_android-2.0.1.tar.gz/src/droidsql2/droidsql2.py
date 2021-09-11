import pandas

def read(path,auto_complete=True):
	if auto_complete==True:
		path='/sdcard/'+path
		
	df=pandas.read_csv(path)
	return df



def save(data,path,mode='a',auto_complete=True,auto_df=False,header=True):
	if auto_complete:
		path='/sdcard/'+path
		
	if auto_df:
		data=pandas.DataFrame(data=data)
	
	data.to_csv(path,mode=mode,index=False,header=header)
	
	
	
def to_df(data):
	df=pandas.DataFrame(data=data)
	return df



class csv_operator:
	
	def __init__(self,df):
		self.df=df
		
	
	
	def new_row(self,data):
		self.df.loc[data[0]]=data[1]
		return self.df
		
		
		
	def new_col(self,data):
		self.df[data[0]]=data[1]
		return self.df
		
		
		
	def set_rowName(self,indexes):
		self.df.index=indexes
		return self.df
		
		
		
	def set_colName(self,columns):
		self.df.columns=columns
		return self.df
		
		
	
	def set_data(self,pos,data):
		row_pos=pos[0]
		col_pos=pos[1]
		self.df.loc[row_pos,col_pos]=data
		return self.df
		
		
		
	def get_data(self,pos):
		return self.df.loc[pos[0],pos[1]]
		
		
	
	def delete(self,name,mode):
		if mode in [0,'row']:
			axis=0
		elif mode in [1,'col']:
			axis=1
		self.df=self.df.drop(name,axis=axis)
		
		
		
	def get_df(self):
		return self.df