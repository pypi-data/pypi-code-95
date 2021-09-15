from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response,redirect
from django.views.decorators.csrf import csrf_exempt
import json
import os
import torch
from . import Util
from FModel.models import Clients
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
save_dir=os.path.join(BASE_DIR, 'static', 'modelfile')

def index(request): 
    context= {}
    context['clients']=Util.getClients()
    context['clients_count']=len(context['clients'])
    return render(request, 'index.html', context)
@csrf_exempt
def client_login(request):
    context= {}
    if request.method == 'POST':
        cname=request.POST.get('clientName')
        key=request.POST.get('key')
        context=Util.getClientId(cname,key)
    return HttpResponse(json.dumps(context),content_type="application/json")
@csrf_exempt
def send_model(request):
    context= {}
    if request.method == 'POST':
        key=request.POST.get('key')
        test_acc=request.POST.get('acc')
        test_loss=request.POST.get('loss')
        modelfile=request.FILES.get('file')
        with  open(os.path.join(save_dir,key), 'wb') as f:
            for chunk in modelfile.chunks():
                f.write(chunk)
        ncl=Clients.objects.filter(Key=key).first()
        if ncl and test_loss:
            if int(test_loss)>0:
                ncl.Loss=test_loss
                ncl.save()
        keys=[cl.Key for cl in Clients.objects.filter(Status=1)]
        result=Util.check_fed_model(save_dir,keys,test_acc,test_loss,10)
        context['result']=result
        print('send_model',context)
    return HttpResponse(json.dumps(context),content_type="application/json")
@csrf_exempt
def get_status(request):
    context= {}
    if request.method == 'POST':
        key=request.POST.get('key')
        keys=[cl.Key for cl in Clients.objects.filter(Status=1)]
        context['modelurl']=''
        context['clientstatus']=Util.check_client(save_dir,key)
        context['result']=Util.check_client_all(save_dir,keys)
        print('context[\'result\']',context['result'])
        if int(context['clientstatus'])==0:
            if os.path.exists(os.path.join(save_dir,'%s_model'%(key))):
                os.rename(os.path.join(save_dir,'%s_model'%(key)),os.path.join(save_dir,'%s_modelb'%(key)))
                context['modelurl']=os.path.join(save_dir,'%s_modelb'%(key)).replace(BASE_DIR,'')
            else:
                Util.check_fed_model(save_dir,keys,0,0,10)
        print(context)
        # Util.addtasklog(ut.save_dir,'get_status',taskid,clientid,'result',context['result'],context['modelurl'],context['clienttrain'])
    return HttpResponse(json.dumps(context),content_type="application/json") 

@csrf_exempt
def changeStatus(request):
    context= {}
    if request.method == 'GET':
        key=request.GET.get('key')
        status=request.GET.get('status')
        context['result']=Util.setClientStatus(key,status)
    return HttpResponse(json.dumps(context),content_type="application/json") 


@csrf_exempt
def deleteclient(request):
    context= {}
    if request.method == 'GET':
        key=request.GET.get('key')
        cl=Clients.objects.filter(Key=key).first()
        if cl:
            cl.delete()
            context['result']=1
    return HttpResponse(json.dumps(context),content_type="application/json") 