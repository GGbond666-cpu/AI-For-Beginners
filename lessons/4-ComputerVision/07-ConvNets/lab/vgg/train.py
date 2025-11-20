import torch.nn as nn
import torch
from torch.utils.tensorboard import SummaryWriter
writer=SummaryWriter("run")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from validation import *

from model import *

from read_data import *
root=""
Data_class,train_loader,test_loader=read_data(root)

def train(model,train_loader,test_loader,epochs,optimizer,loss_func=nn.CrossEntropyLoss(),):
    global best_loss, trigger_times
    step=0
    loss_func=loss_func.to(device)
    model.train()
    for epoch in range(epochs):
        for images_batch,labels_batch in train_loader:
            images_batch=images_batch.to(device)
            labels_batch=labels_batch.to(device)

            outputs=model(images_batch)
            loss=loss_func(outputs,labels_batch)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()


            if step%10==0:
                acc=torch.mean((torch.argmax(outputs,dim=1)==labels_batch).float())
                writer.add_scalar(tag="Acc",scalar_value=acc.item(),global_step=step)
                writer.add_scalar(tag="Loss",scalar_value=loss.item(),global_step=step)
                print(f"Acc={acc}, Loss={loss}")
            if step%200==0:
                print("Test:")
                print(validation(model,test_loader))

            step+=1


        val_acc, val_loss = validation(model,test_loader)
        print("Epoch {} done, validation acc = {}, validation loss = {}".format(epoch,val_acc,val_loss))


model=MyNet().to(device)
optimizer=torch.optim.Adam(model.parameters(),lr=0.001)
train(model,train_loader,test_loader,epochs=10,optimizer=optimizer)