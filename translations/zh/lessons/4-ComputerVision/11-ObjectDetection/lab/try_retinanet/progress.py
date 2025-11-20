from xml_dataset import *
from torchvision.transforms import  transforms
from torch.utils.data.dataloader import DataLoader
from model import  retinanet_model
from train import  train

class_dict={
    "background":0,
    "head":1
}
transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    #一定要添加归一化，不然训练会很慢,因为模型的权重都是再归一化下训练的
])

dataset=xml_dataset("../small_JPEGImages","../small_Annotations",class_dict,transform=transform)
train_size=int(len(dataset)*0.8)
test_size=len( dataset)-train_size
#获得训练集和测试集
train_dataset,test_dataset=torch.utils.data.random_split(dataset,[train_size,test_size])

train_loader=DataLoader(train_dataset,shuffle=True,batch_size=8,num_workers=0,pin_memory=True,
                        collate_fn=lambda x: tuple(zip(*x)))
test_loader=DataLoader(test_dataset,shuffle=True,batch_size=8,num_workers=0,pin_memory=True,
                        collate_fn=lambda x: tuple(zip(*x)))
device="cuda" if torch.cuda.is_available() else "cpu"
retinanet_model=retinanet_model.to(device)

if __name__=="__main__":
    train(retinanet_model,train_loader,device,epochs=10,frequency=10)