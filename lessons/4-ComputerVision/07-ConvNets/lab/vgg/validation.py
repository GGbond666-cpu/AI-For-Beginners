import torch
import torch.nn as nn

def validation(model, test_loader,device,loss_func=nn.CrossEntropyLoss()):
        total_loss = 0
        total_acc = 0
        model.eval()  # 切换模型到验证模式（Dropout层会失效）
        len=0
        with torch.no_grad():
            for images_batch, labels_batch in test_loader:
                len+=1
                images_batch = images_batch.to(device)
                labels_batch = labels_batch.to(device)
                outputs = model(images_batch)
                loss = loss_func(outputs, labels_batch)
                total_loss += loss.item()#每一轮平均的loss
                # top3 = torch.topk(outputs, k=6, dim=1)[1]
                # labels_expand = labels_batch.unsqueeze(1)
                # acc=(top3==labels_expand).any(dim=1).sum()
                acc = (torch.argmax(outputs, dim=1) == labels_batch).mean()
                total_acc += acc
        acc = total_acc / len
        loss = total_loss /  len
        return acc, loss