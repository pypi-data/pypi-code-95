# import matplotlib.pyplot as plt

# class Plot:
#     def __init__(self):
#         pass
#     def mkfig(self,
#         label:str="",
#         title="",
#         width_by_height:tuple=(13.333,7.5),
#         dpi:int=100,
#         font_family="Times New Roman"):
#         '''Calls plt.figure() and passes parameters accordingly.
#         '''
#         plt.figure(num=label, figsize=width_by_height, dpi=dpi)
#         plt.suptitle(title)
#         plt.rcParams["font.family"] = "Times New Roman"
#             # Font not found? Try these commands on Linux:
#             #       sudo apt install msttcorefonts -qq
#             #       rm ~/.cache/matplotlib -rf
#             # Restart IDE

#     def plot(self,
#         data,
#         subplot_number:int=1,
#         marker:str='',
#         data_label:str='',
#         title:str="",
#         xlabel:str="",
#         ylabel:str="",
#         xlim:tuple(int,int)=(None,None),
#         ylim:tuple(int,int)=(None,None)):
#         self.fig, self.ax = plt.subplot(subplot_number)
#         if marker != '' and data_label != '':
#             plt.plot(data, marker, label=data_label)
#         elif marker != '':
#             plt.plot(data, marker)
#         elif data_label != '':
#             plt.plot(data, label=data_label)
#         else:
#             plt.plot(data)
#         if data_label != '':
#             plt.legend()
#         if title != "":
#             plt.title(title)
#         if xlabel != "":
#             plt.xlabel(xlabel)
#         if ylabel != "":
#             plt.ylabel(ylabel)
        
        