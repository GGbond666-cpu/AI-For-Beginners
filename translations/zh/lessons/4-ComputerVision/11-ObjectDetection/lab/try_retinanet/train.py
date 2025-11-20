import torch
#其实好像训练过程倒没有那么难

def train(model,train_loader,device,epochs,frequency=10):
    model=model.to(device)
    optimizer=torch.optim.Adam(model.parameters(),lr=1e-4,weight_decay=1e-5)

    for epoch in range(epochs):
        model.train()

        for i,(imgs,targets) in enumerate(train_loader):

            imgs=[img.to(device) for img in imgs]
            targets=[{k:v.to(device) for k,v in t.items()} for t in targets]
            #训练
            loss_dict=model(imgs,targets)
            loss=sum(loss_dict.values())

            #反向传播+更新
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if i%frequency==0:
                print(f"Epoch: {epoch},i: {i} loss: {loss.item()}")
        if epoch%5==0:  #每5个epoch保存一次模型
            print("saving model...")
            model_path="model_predict"+str(epoch)+".pth"
            torch.save(model.state_dict(),model_path)
        torch.save({
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
        }, f"checkpoint_{epoch}.pth")
