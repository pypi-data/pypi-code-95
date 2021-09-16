import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


def create_df(list_of_models,model_names="none"):
    data=pd.DataFrame()
    if isinstance(list_of_models, list)==False:
        list_of_models=[list_of_models]
    if model_names=="none":
        model_names=["".join(["model_",str(v)]) for v in range(1,len(list_of_models)+2)]
    
    i=0
    for mod in list_of_models:
        # Create dataframe of results summary 
        coef_df = pd.DataFrame(mod.summary().tables[1].data)
        # Drop the extra row with column labels
        coef_df=coef_df.drop(0)
        coef_df.iloc[:,1:]=coef_df.iloc[:,1:].applymap(lambda x:float(x))
        # Add column names
        coef_df.columns=["varname","coef","std_err","t","pvalue","0.25","0.975"]
        coef_df["err"]=coef_df["coef"].apply(lambda x:float(x))-coef_df["0.25"].apply(lambda x: float(x))
        coef_df["model"]=model_names[i]
        data=data.append(coef_df)
        i+=1
    return data




def coeff_plot(data,selected_var=None,show_intercept=True,intercept_name="Intercept",fontsize=12,colors="standard",marker_colors="standard",bar_colors="standard",linewidth=2,markersize=8,marker="^",legend=True,smf=True,orientation="horizontal",
              axis_title=None,figsize=None,xlabel="variables",ylabel="coefficient",manual_axs_lims=None,xticklabels=None,yticklabels=None,return_figure=False):

    """
    data: a pandas dataframe with four columns [coef,err,model,varname]
    show_intercept: show or not intercept coefficient
    
    intercept_name: name of the intercept
    fontsize: fontsize of the text in the figures
    colors: a unique or a list of colors for bar and markers
    marker_colors: a list of colors for markers
    bar_colors: a list of colors for bar
    selected_var:a list-array with the names of the specific variables you want to show or the order
    
    linewidth:width of the bar
    markersize: size of the marker
    marker: type of marker (triangle, point, etc... see: https://matplotlib.org/3.3.3/api/markers_api.html)
    color_line: a unqque or a list of colors for bar
    legend: show legend or not
    axis_title: title of the figure, default is none
    figsize: a tuple (xsize,ysize) for editing the size of the figure. default is 5,10
    xlabel: label of x-axis
    ylabel: label of y-axis
    manual_axs_lims: list of array limits
    xticklabels: list of xticklabels
    yticklabels: list of yticklabels
    return_figure: wether showing directly the fiure or only returning the object
    """


        
        
    ### shape data
    if smf==False:
        if {"coef","model","varname","err"}.issubset(set(data.columns))==False:
            raise Exception("columns of the dataframe are not correct. please make sure the dataframe has columns named [coef, err, model,varname]") 
    else:
        ### shape data
        data=create_df(data)
    
    ### order variable and model
    data.sort_values(["varname","model"],inplace=True,ascending=True)

    ## dimension 
    if figsize==None:
        figsize=(10,5)
        
    ## start plotting
    fig,axs=plt.subplots(figsize=figsize)
    
    
    if show_intercept!=False:
        data.drop((data.loc[data["varname"]==intercept_name]).index,axis=0,inplace=True)
    
    data.reset_index(inplace=True,drop=True)
    if selected_var!=None:
        sorter=selected_var
        data.drop(data.loc[~data["varname"].isin(sorter),:].index,axis=0,inplace=True)
        # Create the dictionary that defines the order for sorting
        sorterIndex = dict(zip(sorter, range(len(sorter))))
        # Generate a rank column that will be used to sort
        # the dataframe numerically
        data['var_rank'] = data['varname'].map(sorterIndex)

        data=data.sort_values(["model","var_rank"],ascending=[True,True]).copy()
    
    ### this is to have the name of the variable
    var_to_show=list(data["varname"].unique())
    ### 
    
    ## index unique combinations of variables
    indx=data.loc[data["varname"].isin(var_to_show),"varname"].drop_duplicates().index

    ### the baseline plot
    if orientation=="horizontal":
        data.loc[indx,:].plot(y="coef",x="varname",kind="scatter",ax=axs,color="none")
    else:
        data.loc[indx,:].plot(x="coef",y="varname",kind="scatter",ax=axs,color="none")


    ### give a 10% margin to axis limits of the plot
    
    ax_min=np.round((data["coef"]-data["err"]).min()*1.10,4)
    ax_max=np.round((data["coef"]+data["err"]).max()*1.10,4)

    if manual_axs_lims!=None:
        ax_min=manual_axs_lims[0]
        ax_max=manual_axs_lims[1]
    
    ### set label name
    axs.set_xlabel(xlabel)
    axs.set_ylabel(ylabel)

    if orientation=="horizontal":
        axs.set_ylim(ax_min,ax_max)
        ## in case ax is rotated and label not specified, invert the names
        if ((xlabel=="variables")&(ylabel=="coefficient"))==True:
            axs.set_xlabel(ylabel)
            axs.set_ylabel(xlabel)
    else:
        axs.set_xlim(ax_min,ax_max)


    
    ## titles and labels
    if axis_title!=None:
        axs.set_title(axis_title)
        
        
    ### collections of model
    list_of_model=[]
    for model in data["model"].unique():
        list_of_model.append(data.loc[data["model"]==model,:])


    std_marker_colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']
    std_bar_colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928'] 

    if colors!="standard":
        if len([colors])==1:
            marker_colors=[colors]*len(list_of_model)
            bar_colors=[colors]*len(list_of_model)
        else:
            marker_colors=colors
            bar_colors=colors

    if marker_colors!="standard":
        if len([marker_colors])==1:
            marker_colors=[marker_colors]*len(list_of_model)
    else:
        marker_colors=std_marker_colors
        
    if bar_colors!="standard":
        if len([bar_colors])==1:
            bar_colors=[bar_colors]*len(list_of_model)
    else:
        bar_colors=std_bar_colors
        
    ## name of model
    list_name_model=data["model"].unique()

    ### positioner
    variable_count=data.groupby("varname",as_index=False)["coef"].count()
    ## keep the order of variables as given
    variable_count=variable_count.set_index("varname").reindex(var_to_show).reset_index(drop=False).copy()
    variable_count["even"]=variable_count["coef"]%2
    distance_between=0.1
    positioner=[]
    for i,row in variable_count.iterrows():
        ## if even
        if row["coef"]%2==0:
              positioner.append([v for v in np.arange(row.name-(row["coef"]/20)+distance_between/2,row.name+(row["coef"]/20)+0.001, distance_between)])
        else:
            positioner.append([v for v in np.arange(row.name-(row["coef"]/20)+distance_between/2,row.name+(row["coef"]/20)+0.001, distance_between)])
    variable_count["positions"]=positioner
    variable_count["counter"]=0

    

    for bar_color,mrk_color,model in zip(bar_colors,marker_colors,list_of_model):
        ### markers
        for i,row in model.iterrows():
            ## plot lines
            x_count=variable_count.loc[variable_count["varname"]==row["varname"],"counter"].iloc[0]
            x_position=variable_count.loc[variable_count["varname"]==row["varname"],"positions"].iloc[0][x_count]
            
            if orientation=="horizontal":
                ## plot bar
                axs.vlines(x=x_position,
                           ymin=row["coef"]-row["err"],
                           ymax=row["coef"]+row["err"],linewidth=linewidth,color=bar_color)
                ###  
                plt.axhline(y=0, color='grey', linestyle='--',linewidth=linewidth/2)
                #axs.hlines(y=0,xmin=-1,xmax=len(var_to_show)+0.5,linewidth=1,linestyle="--",color="grey")
                ## plot markers
                axs.plot(x_position,row["coef"], 
                         color=mrk_color, 
                         marker=marker, 
                         linestyle='dashed',linewidth=linewidth, markersize=markersize)  
            else:
                ## plot bar
                axs.hlines(y=x_position,
                           xmin=row["coef"]-row["err"],
                           xmax=row["coef"]+row["err"],linewidth=linewidth,color=bar_color)
                ###  
                plt.axvline(x=0, color='grey', linestyle='--',linewidth=linewidth/2)
                #axs.hlines(y=0,xmin=-1,xmax=len(var_to_show)+0.5,linewidth=1,linestyle="--",color="grey")
                ## plot markers
                axs.plot(row["coef"],x_position, 
                         color=mrk_color, 
                         marker=marker, 
                         linestyle='dashed',linewidth=linewidth, markersize=markersize)  
                
        ### update the counter
        variable_count.loc[variable_count["varname"].isin(model["varname"].unique()),"counter"]+=1

    ## create legend
    if legend==True:        
        custom_rectangles=[Rectangle((0.2,0.2,0.2),0.2,0.2,color=v) for v in marker_colors]
        axs.legend(custom_rectangles,list_name_model)

    ### set x ticks labels
    if xticklabels!=None:
        axs.set_xticklabels(xticklabels)
    
    ## set yticks labels
    if yticklabels!=None:
        axs.set_yticklabels(yticklabels)

    plt.tight_layout()

    if return_figure==True:
        plt.close(fig)
        return fig
    else:
        return None

