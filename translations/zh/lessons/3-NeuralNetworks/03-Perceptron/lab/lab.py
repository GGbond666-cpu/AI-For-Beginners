# import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
import gzip
import random

def train(positive_examples, negative_examples, num_iterations = 310,lr=0.7):
    num_dims = positive_examples.shape[1]#特征数
    weight = np.zeros((num_dims+1,1)) # 创造初始权重

    pos_count = positive_examples.shape[0]
    neg_count = negative_examples.shape[0]
    positive_examples_bias=np.c_[positive_examples,np.ones(len(positive_examples))]
    negative_examples_bias=np.c_[negative_examples,np.ones(len(negative_examples))]
    report_frequency = 10#统计记录频率
    
    for i in range(num_iterations):
        pos = random.choice(positive_examples_bias)#随机挑选一个正样本
        neg = random.choice(negative_examples_bias)

        z = np.dot(pos, weight)   
        #这里默认学习率为1？
        if z < 0:
            weight = weight + lr*pos.reshape(weight.shape)

        z  = np.dot(neg, weight)
        if z >= 0:
            weight = weight - lr*neg.reshape(weight.shape)
            
        if i % report_frequency == 0:             
            pos_out = np.dot(positive_examples_bias, weight)
            neg_out = np.dot(negative_examples_bias, weight)        
            pos_correct = (pos_out >= 0).sum() / float(pos_count)
            neg_correct = (neg_out < 0).sum() / float(neg_count)
            print("Iteration={}, pos correct={}, neg correct={}".format(i,pos_correct,neg_correct))

    return weight

def accuracy(weights, test_x, test_labels):
    predict = classify(test_x,weights)

    return (predict==test_labels).mean()


with gzip.open('D:\\AI_project\\AI-For-Beginners\\translations\\zh\\lessons\\3-NeuralNetworks\\03-Perceptron\\mnist.pkl.gz', 'rb') as mnist_pickle:
    mnist_tuple = pickle.load(mnist_pickle, encoding='latin1')

# 将元组转换为字典格式（匹配你原代码的键名）
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

# # 归一化到 [0,1]，并确保为 float32（训练/测试/验证一致）
# MNIST['Train']['Features'] = MNIST['Train']['Features'].astype(np.float32) / 256.0
# MNIST['Test']['Features'] = MNIST['Test']['Features'].astype(np.float32) / 256.0
# MNIST['Validation']['Features'] = MNIST['Validation']['Features'].astype(np.float32) / 256.0

MNIST['Train']['Features'] /= MNIST['Train']['Features'].std()
MNIST['Test']['Features'] /= MNIST['Test']['Features'].std()
MNIST['Validation']['Features'] /= MNIST['Validation']['Features'].std()

def set_mnist_pos_other(target_label):
    target_indices = [i for i, j in enumerate(MNIST['Train']['Labels']) 
                          if j == target_label]
    other_indices = [i for i, j in enumerate(MNIST['Train']['Labels']) 
                          if j != target_label]

    positive_images = MNIST['Train']['Features'][target_indices]
    other_images = MNIST['Train']['Features'][other_indices]

    return positive_images, other_images

pos = {}
other = {}
for d in range(10):
    pos[d], other[d] = set_mnist_pos_other(d)

initialized = False
for i in range(10):
    if initialized is False:
        weights=train(pos[i],other[i])
        initialized = True
    else:
        weights=np.c_[weights,train(pos[i],other[i])]

def classify(X,weights):
    X_bais=np.c_[X,np.ones(len(X))]
    score=np.dot(X_bais,weights)
    return np.argmax(score,axis=1) 
X=MNIST["Test"]["Features"][:10]
predict=classify(X,weights)
print(predict)
print(MNIST["Test"]["Labels"][:10])

test_x=MNIST["Test"]["Features"]
test_label=MNIST["Test"]["Labels"]
acc=accuracy(weights,test_x,test_label)
print("ACC:"+"*"*10)
print(acc)
print(test_x.shape)
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# 计算预测结果
predictions = classify(test_x, weights)
# 生成混淆矩阵（10x10）
cm = confusion_matrix(test_label, predictions)

# 可视化
plt.figure(figsize=(10,8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=range(10), yticklabels=range(10))
plt.xlabel('predict')
plt.ylabel('true')
plt.title('confusion matrix')
plt.show()