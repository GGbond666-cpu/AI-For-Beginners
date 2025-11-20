from torchvision import datasets
import torchvision.transforms as transforms
from torch.utils.data.dataloader import DataLoader
from torch.utils.data import random_split
transform=transforms.Compose([transforms.Resize((112,112)),transforms.ToTensor()])

def read_data(root):
    PetDataSets=datasets.ImageFolder(root,transform=transform)
    Data_class=PetDataSets.classes

    data_size=len(PetDataSets)
    train_size=int(data_size*0.8)
    train_dataset,test_dataset=random_split(PetDataSets,[train_size,data_size-train_size])
    train_loader=DataLoader(train_dataset,shuffle=True,batch_size=128,num_workers=2,pin_memory=True)
    test_loader=DataLoader(test_dataset,shuffle=True,batch_size=32,num_workers=2,pin_memory=True)

    return Data_class,train_loader,test_loader