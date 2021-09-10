import torch
import copy
import os
from FModel.models import Clients
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
savefile=os.path.join(BASE_DIR, 'static', 'modelfile','clients.tsv')
#
def getClients():
    clients=Clients.objects.all()
    print('clients',len(clients))
    clientsList=[]
    for cl in clients:
        print(cl.Key)  
        item={}
        item['id']=cl.CID
        item['name']=cl.CName
        item['key']=cl.Key
        item['status']=cl.Status
        item['checked']='checked' if int(cl.Status)==1 else ''
        clientsList.append(item)
    return clientsList
def setClientStatus(key,status):
    result=0
    client=Clients.objects.filter(Key=key).first()
    if client:
        if client.Status!=int(status):
            client.Status=status
            client.save()
            result=1
    return result
def getClientId(cname,key=None):
    print('key00000000',key)
    context={}
    context['result']=0
    if not key.strip():
        count=Clients.objects.count()
        key=getMD5('%s%s'%(count,cname))
        ncl=Clients.objects.create(CName=cname,Key=key,Status=0)
        context['clientid']=ncl.CID
        context['key']=key 
        print(context)
    elif key.strip() and not Clients.objects.filter(Key=key).first():
        ncl=Clients.objects.create(CName=cname,Key=key,Status=0)
        context['clientid']=ncl.CID
        context['key']=key 
    elif Clients.objects.filter(Key=key,Status=1).first():
        context['result']=1
    return context
def average_weights(w):
    """
    Returns the average of the weights.
    """
    w_avg = copy.deepcopy(w[0])
    for key in w_avg.keys():
        for i in range(1, len(w)):
            w_avg[key]=w_avg[key].cpu()
            w_avg[key] +=w[i][key].cpu()
        w_avg[key] = torch.div(w_avg[key], len(w))
    return w_avg

def check_fed_model(save_dir,keys,test_acc=None,test_loss=None,EpochCount=None):
    # addtasklog(save_dir,clientnumber,taskname,'test_acc',test_acc,'test_loss',test_loss,_clientid)
    result=1
    cmodels=[]
    try:
        for key in keys:
            model=torch.load(os.path.join(save_dir,key))
            cmodels.append(model)
        result=3
    except:
        pass
    if result==3:
        avg_model=average_weights(cmodels)
        if avg_model:
            for key in keys:
                try:
                    model=torch.load(os.path.join(save_dir,key))
                    torch.save(avg_model,os.path.join(save_dir,'%s_model'%(key)))
                    os.remove(os.path.join(save_dir,key))
                except:
                    pass
    return result
 
def check_client(save_dir,key):
    # addtasklog(save_dir,'Client_%s'%_clientid)
    result=0
    try:
        if os.path.exists(os.path.join(save_dir,key)):
            model=torch.load(os.path.join(save_dir,key))
            result=1
    except:
        pass
    return result
def check_client_all(save_dir,keys):
    # addtasklog(save_dir,'Client_%s'%_clientid)
    result=1
    try:
        for key in keys:
            model=torch.load(os.path.join(save_dir,key))
        result=3
    except:
        pass
    return result

import hashlib
 
def getMD5(message):
    m = hashlib.md5()
    m.update(message.encode(encoding='utf-8'))
    return m.hexdigest()