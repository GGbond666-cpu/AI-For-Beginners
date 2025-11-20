import torchvision
import torch
retinanet_model=torchvision.models.detection.retinanet_resnet50_fpn(pretrained=True)

# #retinanet本来是针对coco数据集的，所以需要修改最后一层，输出的类别数
num_classes=2
in_features=retinanet_model.head.classification_head.cls_logits.in_channels
anchor=retinanet_model.anchor_generator.num_anchors_per_location()[0]
new_cls_logits=torch.nn.Conv2d(in_features,num_classes*anchor,(3,3),padding=1)
retinanet_model.head.classification_head.cls_logits=new_cls_logits
retinanet_model.head.classification_head.num_classes=num_classes
