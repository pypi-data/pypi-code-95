# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 02:16:58 2021

@author: Dhusor
"""

import torch

def train_validation(Start,End,Path,model,optimizer,criterion,train_loader,validation_loader,
                            all_tranning_loss,all_validation_loss, all_tranning_accuracy, all_validation_accuracy):

    num_epochs=End

    for epoch in range(Start,num_epochs):
        model.train()
        phase = 'training'
        print("------------------------------------------------------------")
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        running_loss = 0.0
        running_corrects = 0
        for inputs, labels in train_loader:
                    
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            running_corrects += torch.sum(preds == labels.data)
            
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = running_corrects.double().item() /len(train_loader.dataset)
        all_tranning_loss.append(loss.item())
        all_tranning_accuracy.append(epoch_acc)


        print("----------------------------Tranning Summary----------------------")
        print('{} Tranning Avg. Loss: {:.4f} Tranning Avg. Acc: {:.4f}'.format(
            phase, epoch_loss, epoch_acc))
        
        model.eval()
        
        with torch.no_grad():
            phase = "validation"
            running_loss = 0.0
            running_corrects = 0
            for inputs, labels in validation_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)

                running_loss += loss.item()
                running_corrects += torch.sum(preds == labels.data)  
                
            epoch_val_loss = running_loss / len(validation_loader)
            epoch_val_acc = running_corrects.double().item() /len(validation_loader.dataset)
            all_validation_loss.append(epoch_val_loss)
            all_validation_accuracy.append(epoch_val_acc)

            print("----------------------------Validation Summary-----------------")
            print('{} Validation Avg. Loss: {:.4f} Validation Avg. Acc: {:.4f}'.format(
                        phase, epoch_val_loss, epoch_val_acc))
            print("------------------------------------------------------------")
            
    
        model.train()

    Path +="trained.pt"
    objects={
        'Epoch': epoch,
        'Model_state': model.state_dict(),
        'Optimizer_state': optimizer.state_dict(),
        'Tranning_loss': all_tranning_loss,
        'Tranning_accuracy': all_tranning_accuracy,
        'Validation_loss': all_validation_loss,
        'Validation_accuracy': all_validation_accuracy,

    }
    torch.save(objects, Path)


from pathlib import Path as pt
device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def run_model(model,train_loader,validation_loader,optimizer,criterion):
    model=model.to(device)
    Start=0
    all_tranning_loss=[]
    all_validation_loss=[]
    all_tranning_accuracy=[]
    all_validation_accuracy=[]

    decision=input('y:start from zero epoch n:after previous epoch: ')
    if decision=='y':
        End=int(input('Enter Number Of Epoch: '))
        Path=input('Enter path to save the model: ')
        train_validation(Start,End,Path,model,optimizer,criterion,train_loader,validation_loader,
                            all_tranning_loss,all_validation_loss, all_tranning_accuracy, all_validation_accuracy)
    
    else:
        load_saved_model=input('Enter Previous Trained Path: ')
        End=int(input('Enter End: '))
        p=pt(load_saved_model)
        if len(load_saved_model) > 1 and p.exists():

            loadedModel = torch.load(load_saved_model, map_location=device)
            model.load_state_dict(loadedModel['Model_state'])

            Start = loadedModel['Epoch'] + 1 
            all_tranning_loss = loadedModel['Tranning_loss'] 
            all_validation_loss = loadedModel['Validation_loss'] 
            all_tranning_accuracy = loadedModel['Tranning_accuracy'] 
            all_validation_accuracy = loadedModel['Validation_accuracy']

            train_validation(Start,End,load_saved_model,model,optimizer,criterion,train_loader,validation_loader,
                            all_tranning_loss,all_validation_loss, all_tranning_accuracy, all_validation_accuracy)

