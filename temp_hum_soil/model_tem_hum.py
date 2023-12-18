import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization, Activation
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split

from mltu.tensorflow.callbacks import Model2onnx

data_url = 'G:\PTIT\IOT\html\\temp_hum_soil\TARP.csv'
metadata_df = pd.read_csv(data_url, sep=',')

X_train = metadata_df[['soil', 'temp', 'hum']].astype(float).values
Y_train = metadata_df['Status'].astype(float).values

X_train, X_test, Y_train, Y_test = train_test_split(X_train, Y_train, test_size=0.2)

# Xây dựng mô hình
model = Sequential()
model.add(Dense(32, input_dim=X_train.shape[1]))
model.add(Activation('relu'))
model.add(Dense(64))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(Dense(128))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(Dropout(0.2))
model.add(Dense(256))
model.add(Activation('relu'))
model.add(Dense(1, activation='sigmoid'))

from keras.optimizers import Adam
optimizer = Adam(learning_rate=0.001)
model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

model.fit(X_train, Y_train, epochs=200, batch_size=64)
Model2onnx.model2onnx(model, 'temp_hum_soil\model.onnx')

loss = model.evaluate(X_test, Y_test)
print("Mean Squared Error (Test):", loss)

X_new = [[88,15.72,96]]
Y_pred = model.predict(X_new)
print(Y_pred)
X_new = [[30,16.09,96]]
Y_pred = model.predict(X_new)
print(Y_pred)
X_new = [[2,18.82,20.79]]
Y_pred = model.predict(X_new)
print(Y_pred)


