# 
# 
# %%
from pandas.io.json import json_normalize
import pandas as pd
import json,os,copy
from IPython.display import display



# %%
def buildSchPart(inDF:pd.DataFrame)->str:
    schpart=inDF.to_json(orient='index')
    parsed = json.loads(schpart)
    json_string = json.dumps(parsed)
    return json_string[1:-1]

def buildAddJsonPart(inDF)->str:
    json_str = inDF.to_json(orient='index')
    parsed = json.loads(json_str)
    json_string = json.dumps(parsed) 
    json_string = "\""+"additionalProperty:"+"\": "+json_string
    return json_string

def merge_smallestpart(sch,add)->str:
    return sch+','+add

def buildDifferentMetaParts(nameList,eachLisfWithsch_add)->str:
    metas_json=""
    for single_name in nameList:
        metas_json=metas_json+"\""+single_name+"\": {"
        metas_json=metas_json+eachLisfWithsch_add[nameList.index(single_name)]+"},"
    return metas_json[:-1]
    
def addTopestLevel(topName,eachMetaChunk)->str: 
    top_json="{"+"\""+topName+"\": {"
    top_json=top_json+eachMetaChunk+"}}"
    return top_json

def display_current_JSONDF():
    for i in range(len(Working_on_sch)):
        display('Chunk name: '+list(Working_on_DF.index)[i])
        display(Working_on_sch[i])
        display(Working_on_add[i])
        display('----------------------------------------------------------------')

def save_to_json():
    Chunks=[]
    for i in range(len(chunks_list)):
        smallChunk=merge_smallestpart(buildSchPart(Working_on_sch[i]),buildAddJsonPart(Working_on_add[i]))
        Chunks.append(smallChunk)
    final_json=[addTopestLevel(topest_name,buildDifferentMetaParts(chunks_list,Chunks))]
    with open('output.json', 'w') as f:    
        for item in final_json:                  
            f.write("%s\n" % item)

def editDFs(inname:str,inValue:str):
    if inname in name_sch.keys():
        for i in range(len(name_sch[inname])):
            chunkname=name_sch[inname][i][0]
            colname=name_sch[inname][i][1]
            for j in range(len(chunks_list)):
                if inname in name_sch.keys():
                    if chunks_list[j]==chunkname:
                        Working_on_sch[j].loc['SchemaMetadata',colname]=inValue
    if inname in name_add.keys():
        for i in range(len(name_add[inname])):
            chunkname=name_add[inname][i][0]
            indexname=name_add[inname][i][1]
            for j in range(len(chunks_list)):
                if chunks_list[j]==chunkname and indexname in Working_on_add[j].index:
                    Working_on_add[j].loc[indexname,'value']=inValue
def dealWithInput(inStr:str):
    if "?" == inStr[0]:
        if inStr[1:] in all_name.keys():
            return all_name[inStr[1:]]
        else:
            return 'Can not find the description of the name'
    if ">" in inStr:
        namePart=inStr[0:inStr.index(">")]
        valuepart=inStr[inStr.index(">")+1:]
        if namePart in all_name.keys():
            editDFs(namePart, valuepart)
            return 'Changed value'
        else:
            return 'Can not find the input name'
    if inStr=='!save':
        save_to_json()
        return 'Saved to json file!'
    if inStr=='!import':
        csvname=input('Input the csv file name')
        csvf=pd.read_csv(csvname)
        for i in csvf.columns:
            if i in all_name.keys():
                editDFs(i,str(csvf.loc[0,i]))
            else:
                print('found a data not in the defined names',[i,str(csvf.loc[0,i])])


# %%
temName=input('input template name')
#temName='powerplant_json_template.json'
temDF=pd.read_json(temName,orient='columns')
Working_on_DF=copy.deepcopy(temDF)
topest_name=Working_on_DF.columns[0]
chunks_list=list(Working_on_DF.index)
Working_on_sch=[]
Working_on_add=[]
totalname=[]
for s in chunks_list:
    Working_on_sch.append(pd.DataFrame(Working_on_DF.loc[s,topest_name]['SchemaMetadata'],index=['SchemaMetadata']))
    Working_on_add.append(pd.DataFrame(Working_on_DF.loc[s,topest_name]['additionalProperty']).T)
print('Load template file done!')
#find name hidden in schema part
name_sch={}
name_add={}
all_name={}
for i in range(len(chunks_list)):
    s_sch=Working_on_sch[i]
    for column in s_sch.columns:
        if "$" in s_sch.loc['SchemaMetadata',column]:
            fullStr=s_sch.loc['SchemaMetadata',column]          
            name_str=fullStr[fullStr.index('$')+1:fullStr.index('>')]
            if name_str not in name_sch:
                name_sch[name_str]=[[chunks_list[i],column]]
            else:
                name_sch[name_str].append([chunks_list[i],column])
            if name_str not in all_name:
                all_name[name_str]=s_sch.loc['SchemaMetadata','description']+': '+column
            else:
                all_name[name_str]=all_name[name_str]+', '+s_sch.loc['SchemaMetadata','description']+': '+column

#find name in additional part
for i in range(len(chunks_list)):
    s_app=Working_on_add[i]
    for j in s_app.index:
        if 'value' in s_app.columns:
            if "$" in s_app.loc[j,'value']:
                fullStr=s_app.loc[j,'value']
                name_str=fullStr[fullStr.index('$')+1:fullStr.index('>')]
                if name_str not in all_name:
                    all_name[name_str]=s_app.loc[j,'description']
                    if name_str not in name_add:
                        name_add[name_str]=[[chunks_list[i],j]]
                    else:
                        name_add[name_str].append([chunks_list[i],j])
                else:
                    all_name[name_str]=all_name[name_str]+', '+s_app.loc[j,'description']
                    if name_str not in name_add:
                        name_add[name_str]=[[chunks_list[i]]]
                    else:
                        name_add[name_str].append([chunks_list[i],j])
print('load all name done!')


# %%
exitFlag=False
while exitFlag!=True:
    os.system("clear")
    display_current_JSONDF()
    inputStr=input('Input the command, use ?name to search detailed description, xxx>xxxx to manual base on name, !import to load a csv file,!save to save json file, !exit to exit')  
    returnResults=dealWithInput(inputStr)
    print(returnResults)
    if inputStr=='!exit':
        exitFlag=True


