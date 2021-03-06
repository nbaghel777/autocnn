import keras
from keras.datasets import mnist
from keras.layers.normalization import BatchNormalization
from sklearn.model_selection import train_test_split
from keras.models import *
from keras.layers import *
from keras.callbacks import *
from keras.layers.recurrent import *
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.model_selection import RepeatedKFold

!pip install git+https://github.com/nbaghel777/autocnn

import warnings
warnings.filterwarnings('ignore')

import numpy as np
RUN = 1
DATA_DIR = './speech_commands_v0.01'

def augtime(xdatat,vectorlength):
  X_data=[]
  for i in range(0,len(xdatat)):
    if len(xdatat[i])<vectorlength:
      tem=np.append(xdatat[i],xdatat[i][0:(vectorlength-len(xdatat[i]))])
      while len(tem)<vectorlength:
        tem=np.append(tem,xdatat[i][0:(vectorlength-len(tem))])
    else:
      tem=xdatat[i]
    X_data=np.append(X_data,tem,axis=0)
  X_test=np.reshape(X_data,(len(xdatat),vectorlength,1))
  return X_test

def autocnn_model(size, num_cnn_layers):
    NUM_FILTERS = 32
    KERNEL = 3
    MAX_NEURONS = 120
    model = Sequential()
    
    for i in range(1, num_cnn_layers+1):
        if i == 1:
            model.add(Conv1D(NUM_FILTERS*i, KERNEL, input_shape=size, activation='relu', padding='same'))
        else:
            model.add(Conv1D(NUM_FILTERS*i, KERNEL, activation='relu', padding='same'))
            model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(int(MAX_NEURONS), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(int(MAX_NEURONS/2), activation='relu'))
    model.add(Dense(4, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def cnn_model(size, num_cnn_layers):
  m = Sequential()
  m.add(Conv1D(filters=64, kernel_size=3, strides=2, padding='valid', activation='relu', input_shape=size))
  m.add(BatchNormalization()) 
  m.add(Conv1D(filters=64, kernel_size=3, strides=2, padding='valid', activation='relu'))
  m.add(BatchNormalization())
  m.add(Conv1D(filters=64, kernel_size=3, strides=2, padding='valid', activation='relu'))
  m.add(BatchNormalization())
  m.add(Conv1D(filters=64, kernel_size=3, strides=2, padding='valid', activation='relu')) 
  m.add(BatchNormalization())
  m.add(Conv1D(filters=64, kernel_size=3, strides=2, padding='valid', activation='relu'))
  m.add(BatchNormalization())
  m.add(Conv1D(filters=64, kernel_size=3, strides=3, padding='valid', activation='relu'))
  m.add(BatchNormalization())
  m.add(Conv1D(filters=32, kernel_size=3, strides=2, padding='valid', activation='relu'))
  m.add(BatchNormalization())
  m.add(MaxPooling1D(pool_size=2))
  m.add(Dropout(0.15))
  m.add(Flatten())
  m.add(Dense(128, activation='relu'))
  m.add(Dropout(0.3))
  m.add(Dense(3, activation='softmax'))
  m.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])  
  #m.summary()
  return m

#set early stopping criteria
pat = 5 #this is the number of epochs with no improvment after which the training will stop
early_stopping = EarlyStopping(monitor='val_loss', patience=pat, verbose=1)

#define the model checkpoint callback -> this will keep on saving the model as a physical file
model_checkpoint = ModelCheckpoint('fas_mnist_1.h5', verbose=0, save_best_only=True)

#define a function to fit the model
def fit_and_evaluate(t_x, val_x, t_y, val_y, EPOCHS=20, BATCH_SIZE=128):
    model = None
    model = autocnn_model((2400,1),7)
    results = model.fit(t_x, t_y, epochs=EPOCHS, batch_size=BATCH_SIZE, callbacks=[early_stopping, model_checkpoint], 
              verbose=1, validation_data=(val_x, val_y))  
    print("Val_loss,Val_acc: ", model.evaluate(val_x, val_y))
    return results, model

def modelresults(model,xt, yt):
  y_pred_keras = model.predict(xt)
  yp=np.round(y_pred_keras, 2)
  yt=np.argmax(yt, 1)
  yp=np.argmax(yp, 1)
  print(classification_report(yt, yp))

  #function to draw confusion matrix
  conf_matx = confusion_matrix(yt, yp)
  sns.heatmap(conf_matx, annot=True,annot_kws={"size": 12},fmt='g', cbar=False, cmap="viridis")
  plt.show()
 
  #fpr_keras0, tpr_keras0, thresholds_keras0=roc_curve(y_test[:,0],y_pred_keras[:,0])
  #auc_keras0 = auc(fpr_keras0, tpr_keras0)

  #fpr_keras1, tpr_keras1, thresholds_keras1=roc_curve(y_test[:,1],y_pred_keras[:,1])
  #auc_keras1 = auc(fpr_keras1, tpr_keras1)

  #plt.plot([0,1],[0,1],'k--')
  #plt.plot(fpr_keras0, tpr_keras0, label='keras(area={:.3f})'.format(auc_keras0))
  #plt.plot(fpr_keras1, tpr_keras1, label='keras(area={:.3f})'.format(auc_keras1))
  #plt.title('ROC Curve')
  #plt.xlabel('False positive rate')
  #plt.ylabel('True positive rate')
  #plt.xlabel('Epoch')
  #plt.legend(loc='best')
  #plt.show()

  #return conf_matx

X1 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh1data.npy",allow_pickle=True)
X2 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh2data.npy",allow_pickle=True)
X3 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh3data.npy",allow_pickle=True)
X4 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh4data.npy",allow_pickle=True)
X5 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh5data.npy",allow_pickle=True)
X6 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh6data.npy",allow_pickle=True)
X7 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh7data.npy",allow_pickle=True)
X8 = np.load("/content/drive/My Drive/Colab Notebooks/abr/cnnprocessedh8data.npy",allow_pickle=True)

xdata = np.append(X1,X2,axis=0)
xdata = np.append(xdata,X3,axis=0)
xdata = np.append(xdata,X4,axis=0)
xdata = np.append(xdata,X5,axis=0)
xdata = np.append(xdata,X6,axis=0)
xdata = np.append(xdata,X7,axis=0)
xdata = np.append(xdata,X8,axis=0)

#xdata=X1
vectorlength=2500
X_data=augtime(xdata,vectorlength)

Y_data=[0]*16+[1]*8+[0]*8+[1]*12+[2]*12+[3]*8
Y_data=Y_data+[0]*5+[0]*24+[1]*20
Y_data=Y_data+[0]*20+[1]*4+[0]*4+[1]*4+[0]*4+[1]*8+[3]*4+[2]*8+[3]*20+[2]*4
Y_data=Y_data+[0]*28+[1]*4+[0]*4+[3]*4+[2]*4+[3]*16+[2]*4
Y_data=Y_data+[1]*4+[0]*4+[1]*4+[0]*24+[1]*4+[0]*8+[1]*8+[2]*12+[3]*4+[2]*4+[3]*16
Y_data=Y_data+[1]*32+[0]*4+[1]*8
Y_data=Y_data+[0]*20+[1]*4+[0]*12+[1]*8+[0]*4+[1]*12+[2]*4+[3]*20+[2]*4+[3]*4+[2]*12+[3]*12
Y_data=Y_data+[0]*12+[1]*28+[3]*4+[2]*8+[3]*12

Y_data = keras.utils.to_categorical(Y_data, num_classes=4)

n_folds=10
epochs=50
batch_size=5

#save the model history in a list after fitting so that we can plot later
model_history = [] 

#from sklearn.svm import SVC
#svclassifier = SVC(kernel='linear')
#svclassifier.fit(x_train, y_train)
#y_pred = svclassifier.predict(x_test)
#print(classification_report(y_test, y_pred))

model=[]
from sklearn.model_selection import KFold 
kf = RepeatedKFold(n_splits=5, n_repeats=1, random_state=None) 

for train_index, test_index in kf.split(X_data):
      #print("Train:", train_index, "Validation:",test_index)
      t_x, val_x, t_y, val_y = X_data[train_index], X_data[test_index], Y_data[train_index], Y_data[test_index]
      #val_y= Y_data[test_index]
      result,model=fit_and_evaluate(t_x, val_x, t_y, val_y, epochs, batch_size)
      model_history.append(result)
      modelresults(model,val_x,val_y)

#for i in range(n_folds):
#    print("Training on Fold: ",i+1)
#    t_x, val_x, t_y, val_y = train_test_split(x_train, y_train, test_size=0.1,random_state = np.random.randint(1,1000, 1)[0])
    

model.summary()
        
print("======="*12, end="\n\n\n")

#Load the model that was saved by ModelCheckpoint

plt.title('Train Accuracy vs Val Accuracy')
plt.plot(model_history[0].history['accuracy'], label='Train Accuracy Fold 1', color='black')
plt.plot(model_history[0].history['val_accuracy'], label='Val Accuracy Fold 1', color='black', linestyle = "dashdot")
plt.plot(model_history[1].history['accuracy'], label='Train Accuracy Fold 2', color='red', )
plt.plot(model_history[1].history['val_accuracy'], label='Val Accuracy Fold 2', color='red', linestyle = "dashdot")
plt.plot(model_history[2].history['accuracy'], label='Train Accuracy Fold 3', color='green', )
plt.plot(model_history[2].history['val_accuracy'], label='Val Accuracy Fold 3', color='green', linestyle = "dashdot")
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.show()

plt.title('Train Loss vs Val Loss')
plt.plot(model_history[0].history['loss'], label='Train Loss Fold 1', color='black')
plt.plot(model_history[0].history['val_loss'], label='Val Loss Fold 1', color='black', linestyle = "dashdot")
plt.plot(model_history[1].history['loss'], label='Train Loss Fold 2', color='red', )
plt.plot(model_history[1].history['val_loss'], label='Val Loss Fold 2', color='red', linestyle = "dashdot")
plt.plot(model_history[2].history['loss'], label='Train Loss Fold 3', color='green', )
plt.plot(model_history[2].history['val_loss'], label='Val Loss Fold 3', color='green', linestyle = "dashdot")
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()

# serialize model to JSON
model_json = model.to_json()
with open("abr.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("abr.h5")
print("Saved model to disk")

model.save('abr.model')
