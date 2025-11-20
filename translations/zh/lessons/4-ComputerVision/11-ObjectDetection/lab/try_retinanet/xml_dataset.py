import PIL.Image as Image

import torch
import os

import xml.etree.ElementTree as ET
class xml_dataset(torch.utils.data.Dataset):
    # 初始化,需要传入图片路径和标记路径和需要的transform
    def __init__(self,imgs_path,xmls_path,class_dict,transform=None):
        self.imgs_path = imgs_path
        self.xmls_path = xmls_path
        self.transform = transform
        self.class_dict=class_dict
        #提取以特定后缀结尾的文件
        self.img_list=[img for img in os.listdir(imgs_path) if img.endswith((".jpg",".png", ".jpeg", ".JPG", ".PNG", ".JPEG"))]

    def __len__(self):
        return len(self.img_list)

    def get_xml_infor(self,xml_path,class_dict,w,h ):
        tree=ET.parse(xml_path)
        root=tree.getroot()#获取根节点

        bbox=[]
        labels=[]
        for obj in root.findall("object"):
            #找到里面的bndbox
            bndbox=obj.find("bndbox")
            xmin=float(bndbox.find("xmin").text)#找都后获取用text获取值
            ymin=float(bndbox.find("ymin").text)
            xmax=float(bndbox.find("xmax").text)
            ymax=float(bndbox.find("ymax").text)

            xmin = max(0,min(xmin, w - 1))
            xmax = max(0,min(xmax, w - 1))
            ymin = max(0,min(ymin, h - 1))
            ymax = max(0,min(ymax, h - 1))
            #防止越界

            bbox.append([xmin,ymin,xmax,ymax])

            name=obj.find("name").text
            labels.append(class_dict[name])

        return bbox,labels

    def __getitem__(self, idx):
        img_name = self.img_list[idx]
        img_path=os.path.join(self.imgs_path,img_name)

        xml_name=img_name.split(".")[0]+".xml"#获取xml文件名
        xml_path=os.path.join(self.xmls_path,xml_name)

        img=Image.open(img_path).convert("RGB")#默认模式是RGB
        w,h=img.size
        bbox,labels=self.get_xml_infor(xml_path,self.class_dict,w,h)
        targets={#官方要求targets有五个
            "boxes":torch.tensor(bbox,dtype=torch.float32),
            "labels":torch.tensor(labels,dtype=torch.int64),
            "image_id":torch.tensor(idx,dtype=torch.int64),
            "area":(torch.tensor(bbox,dtype=torch.float32)[:,3]-torch.tensor(bbox,dtype=torch.float32)[:,1])*(torch.tensor(bbox,dtype=torch.float32)[:,2]-torch.tensor(bbox,dtype=torch.float32)[:,0]),
            "iscrowd": torch.zeros((len(labels),), dtype=torch.int64)#需要标注框内是不是有一群人
        }

        if self.transform:
            img=self.transform(img)

        return img,targets
