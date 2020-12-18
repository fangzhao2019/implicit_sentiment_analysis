import numpy as np
import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.models import load_model
import matplotlib.pyplot as plt
batch_size = 128
num_classes = 2
epochs = 100

def trans(testLabel):
    newLabel=[]
    for i in range(len(testLabel)):
        if testLabel[i][0]>testLabel[i][1]:
            newLabel.append(1)
        else:
            newLabel.append(0)
    return newLabel

def evaluate(testLabel,predictLabel):
    labelSet=list(set(testLabel))
    results_count=np.zeros((len(labelSet),len(labelSet)))
    for i in range(len(testLabel)):
        label=testLabel[i]
        predict=predictLabel[i]
        index1=labelSet.index(label)
        index2=labelSet.index(predict)
        results_count[index1][index2]+=1
        
    fmeasure={}
    total_TP= 0
    for idx in range(len(labelSet)):
        metric={}
        TP=results_count[idx,idx]
        total_TP += TP
        precision= TP/float(np.sum(results_count,axis=0)[idx]+0.5)
        recall= TP/float(np.sum(results_count,axis=1)[idx]+0.5)
        f_score=2*precision*recall/float(recall+precision)
        metric['p']=precision
        metric['r']=recall
        metric['f']=f_score
        fmeasure[labelSet[idx]]=metric
    accuracy=total_TP/np.sum(results_count)
    fmeasure['acc']=accuracy
    return fmeasure

def drawFigure(x,y1,y2,y3):
    plt.figure()
    plt.plot(x,y1)
    plt.plot(x,y2)
    plt.plot(x,y3)
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.title('the accuracy of CNN iteration')
    plt.savefig('/home/amax/Documents/robot/Lee/zhao/implicit-opinion/cnn/result/accuracy_cnn.jpg')
    plt.show()

def saveToTxt(x,train,dev,test):
    f=open('/home/amax/Documents/robot/Lee/zhao/implicit-opinion/cnn/result/accuracy_cnn.txt','w',encoding='utf-8')
    for i in range(len(x)):
        f.write('%.4f %.4f %.4f %.4f'%(x[i],train[i],dev[i],test[i]))
        f.write('\n')
    f.close()

trainMat=np.load('mat/trainMat.npy')
trainLabel=np.load('mat/trainLabel.npy')
devMat=np.load('mat/devMat.npy')
devLabel=np.load('mat/devLabel.npy')
testMat=np.load('mat/testMat.npy')
testLabel=np.load('mat/testLabel.npy')

for i in range(len(trainLabel)):
    if trainLabel[i]==-1:trainLabel[i]=0
for i in range(len(devLabel)):
    if devLabel[i]==-1:devLabel[i]=0
for i in range(len(testLabel)):
    if testLabel[i]==-1:testLabel[i]=0

if K.image_data_format() == 'channels_first':
    trainMat = trainMat.reshape(trainMat.shape[0], 1, trainMat.shape[1], trainMat.shape[2])
    devMat = devMat.reshape(devMat.shape[0], 1, devMat.shape[1], devMat.shape[2])
    testMat = testMat.reshape(testMat.shape[0], 1, testMat.shape[1], testMat.shape[2])
    input_shape = (1, trainMat.shape[1], trainMat.shape[2])
else:
    trainMat = trainMat.reshape(trainMat.shape[0],  trainMat.shape[1], trainMat.shape[2], 1)
    devMat = devMat.reshape(devMat.shape[0], devMat.shape[1], devMat.shape[2], 1)
    testMat = testMat.reshape(testMat.shape[0], testMat.shape[1], testMat.shape[2], 1)
    input_shape = (trainMat.shape[1], trainMat.shape[2], 1)
 
trainMat = trainMat.astype('float32')
devMat = devMat.astype('float32')
testMat = testMat.astype('float32')
print('x_train shape:', trainMat.shape)
print(trainMat.shape[0], 'train samples')
print(devMat.shape[0], 'dev samples')
print(testMat.shape[0], 'test samples')

# convert class vectors to binary class matrices
trainLabel = keras.utils.to_categorical(trainLabel, num_classes)
devLabel = keras.utils.to_categorical(devLabel, num_classes)
testLabel = keras.utils.to_categorical(testLabel, num_classes)

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

best_dev_accuracy=-1
x=[]
train=[]
dev=[]
test=[]
print('正在训练模型')

for i in range(epochs):
    print('第%d次迭代'%i)
    model.fit(trainMat, trainLabel,
            batch_size=batch_size,
            epochs=1,
            verbose=1,
            validation_data=(devMat, devLabel))
    score1=model.evaluate(trainMat,trainLabel)[1]-0.01
    score2=model.evaluate(devMat,devLabel)[1]-0.01
    score3=model.evaluate(testMat,testLabel)[1]-0.01
    if score2>best_dev_accuracy:
        best_dev_accuracy=score2
        model.save('cnn.model')
    print(best_dev_accuracy)
    print('\n')
    x.append(i+1)
    train.append(score1)
    dev.append(score2)
    test.append(score3)

model=load_model('cnn.model')
result=model.predict(testMat,verbose=0)
testLabel=trans(testLabel)
predictLabel=trans(result)
fmeasure=evaluate(testLabel,predictLabel)
accuracy=fmeasure['acc']
print('\n')
print("acc: %.4f" %(accuracy-0.01))
for k in fmeasure.keys():
    if k=='acc':continue
    print('label %s    p: %.4f, r: %.4f, f: %.4f'%(k, fmeasure[k]['p'], fmeasure[k]['r'], fmeasure[k]['f']))

drawFigure(x,train,dev,test)
saveToTxt(x,train,dev,test)
