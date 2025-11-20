def validation(model,test_loader,device):
    model.eval()
    for i,(imgs,_) in enumerate(test_loader):
        imgs=[img.to(device) for img in imgs]
        predict=model(imgs)

        prediction=[{k:v.to(device) for k,v in t.items() }for t in predict]
        #获取每一个的预测结果
