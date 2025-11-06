import pickle
import gzip  # 导入gzip模块处理压缩文件
from sklearn.model_selection import train_test_split
from torch.utils.tensorboard import SummaryWriter
from myclass import *
# 先通过gzip.open解压，再用pickle.load读取
with gzip.open('mnist.pkl.gz', 'rb') as f:
    mnist_tuple = pickle.load(f, encoding='latin1')  # encoding='latin1' 兼容旧版本保存的数据

MNIST = {
    'Train': {
        'Features': mnist_tuple[0][0],  # 训练集特征（X_train）
        'Labels': mnist_tuple[0][1]     # 训练集标签（y_train）
    },
    'Test': {
        'Features': mnist_tuple[1][0],  # 测试集特征（X_test）
        'Labels': mnist_tuple[1][1]     # 测试集标签（y_test）
    },
    'Validation': {  # 原数据集通常包含验证集，可选保留
        'Features': mnist_tuple[2][0],
        'Labels': mnist_tuple[2][1]
    }
}

def show_weight_abs(Net):
    for layer in Net.layers:
        if 'update' in layer.__dir__():
            abs_w=np.abs(layer.W)
            print(np.argmax(abs_w,axis=1))

def get_loss_acc(Net,test,labels,loss=CrossEntropyLoss()):
    p = Net.forward(test)
    l = loss.forward(p,labels)
    pred = np.argmax(p,axis=1)
    acc = (pred==labels).mean()
    return l,acc

labels = MNIST['Train']['Labels']
data = MNIST['Train']['Features']
features_train, features_test, labels_train, labels_test = train_test_split(data,labels,test_size=0.2)

print(f"Train samples: {len(features_train)}, test samples: {len(features_test)}")

Net1=Net()
Net1.add(Linear(784,10))
Net1.add(Softmax())
loss_function=CrossEntropyLoss()
#注意这里我需要手动分批次

Net2=Net()
Net2.add(Linear(784,300))
Net2.add(ReLU())
Net2.add(Linear(300,10))
Net2.add(Softmax())

Net3=Net()
Net3.add(Linear(784,256))
Net3.add(Tanh())
Net3.add(Linear(256,128))
Net3.add(Tanh())
Net3.add(Linear(128,10))
Net3.add(Softmax())


batch_size=100
lr=0.01
step=0
writer1=SummaryWriter("log1")
writer2=SummaryWriter("log2")
writer3=SummaryWriter("log3")
epochs =1
for epoch in range(epochs):
    for i in range(0,len(features_train),batch_size):
        x_batch=features_train[i:i+batch_size]
        l_batch=labels_train[i:i+batch_size]
        y=Net1.forward(x_batch)
        loss=loss_function.forward(y,l_batch)
        dy=loss_function.backward(loss)
        Net1.backward(dy)
        Net1.update(lr)
        if step%10==0:
            x_pre=np.argmax(y,axis=1)
            acc=(x_pre==l_batch).mean()
            writer1.add_scalar("acc",acc,i)
            print(f"step {step},Loss: {loss},Acc:{acc}")
            show_weight_abs(Net1)
        step+=1
writer1.close()
step=0

for epoch in range(epochs):
    for i in range(0,len(features_train),batch_size):
        x_batch=features_train[i:i+batch_size]
        l_batch=labels_train[i:i+batch_size]
        y=Net2.forward(x_batch)
        loss=loss_function.forward(y,l_batch)
        dy=loss_function.backward(loss)
        Net2.backward(dy)
        Net2.update(lr)
        if step%10==0:
            x_pre=np.argmax(y,axis=1)
            acc=(x_pre==l_batch).mean()
            writer2.add_scalar("acc",acc,i)
            print(f"step {step},Loss: {loss},Acc:{acc}")
            show_weight_abs(Net2)
        step+=1
writer2.close()
step=0
for epoch in range(epochs):
    break
    for i in range(0, len(features_train), batch_size):
        x_batch = features_train[i:i + batch_size]
        l_batch = labels_train[i:i + batch_size]
        y = Net3.forward(x_batch)
        loss = loss_function.forward(y, l_batch)
        dy = loss_function.backward(loss)
        Net3.backward(dy)
        Net3.update(lr)
        if step % 10 == 0:
            x_pre = np.argmax(y, axis=1)
            acc = (x_pre == l_batch).mean()
            writer3.add_scalar("acc", acc, i)
            #print(f"step {step},Loss: {loss},Acc:{acc}")
        step += 1
writer3.close()

print("test:"+"="*70)
l1,acc1=get_loss_acc(Net1,features_test,labels_test,loss_function)
print(f"Net 1 loss:{l1},acc:{acc1}")
l2,acc2=get_loss_acc(Net2,features_test,labels_test,loss_function)
print(f"Net 2 loss:{l2},acc:{acc2}")
l2,acc2=get_loss_acc(Net3,features_test,labels_test,loss_function)
print(f"Net 3 loss:{l2},acc:{acc2}")