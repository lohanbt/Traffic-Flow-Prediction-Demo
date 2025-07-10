from keras.layers import Dense, LSTM, GRU, Dropout, Input
from keras.models import Sequential
from keras.models import Model
from keras import regularizers
from tcn import TCN
from tensorflow.keras.losses import MSE
import numpy as np
from tensorflow.keras.regularizers import L2


# GET LSTM MODEL
def get_lstm(input_shape):

  model = Sequential()
  model.add(LSTM(128, input_shape=input_shape, return_sequences=True))
  model.add(LSTM(64))
  model.add(Dropout(0.2))
  model.add(Dense(1, activation='sigmoid'))

  return model

# GET GRU MODEL
def get_gru(input_shape):
  model = Sequential()
  model.add(GRU(128, input_shape=input_shape, return_sequences=True))
  model.add(GRU(64))
  model.add(Dropout(0.2))
  model.add(Dense(1, activation='sigmoid'))

  return model

# GET 1 AUTOENCODER
def get_each_sae(input_dim, layer_1, layer_2, learning_rate):

  model = Sequential()

  model.add(Dense(
    layer_1, input_dim=input_dim, 
  
    activity_regularizer=L2(learning_rate),
    activation="relu"
  ))  
  model.add(Dense(
    layer_2, 
    activity_regularizer=L2(learning_rate),
    activation="relu"
  ))
  model.add(Dense(
    layer_1,
    activation="relu", 
    activity_regularizer=L2(learning_rate),
  ))
  model.add(Dense(
    input_dim,
    activation="sigmoid", 
    activity_regularizer=L2(learning_rate)
  ))
  
  return model


# GET & TRAIN STACKED AUTOENCODER
def train_saes_2(X_train, y_train, config):


  sae1 = get_each_sae(12, 60, 60, 0.00001)
  sae1.compile(loss=MSE, optimizer="adam", metrics=['accuracy'])
  sae1.fit(X_train, X_train, batch_size=config["batch"], epochs=config["epochs"], validation_split=0.05)

  sae2_input = sae1.predict(X_train)
  sae2_input = np.concatenate((sae2_input, X_train))

  sae2 = get_each_sae(12, 60, 60, 0.00001)
  sae2.compile(loss=MSE, optimizer="adam", metrics=['accuracy'])
  sae2.fit(sae2_input, sae2_input, batch_size=config["batch"], epochs=config["epochs"], validation_split=0.05)

  sae3_input = sae2.predict(sae2_input)
  sae3_input = np.concatenate((sae3_input, sae2_input))

  sae3 = get_each_sae(12, 60, 60, 0.00001)
  sae3.compile(loss=MSE, optimizer="adam", metrics=['accuracy'])
  sae3.fit(sae3_input, sae3_input, batch_size=config["batch"], epochs=config["epochs"], validation_split=0.05)
  
  saes = Sequential()
  for layer in sae1.layers:
    saes.add(layer)
  for layer in sae2.layers:
    saes.add(layer)
  for layer in sae3.layers:
    saes.add(layer)
  saes.add(Dropout(0.2))

  saes.add(Dense(1, activation='sigmoid'))
  saes.compile(loss=MSE, optimizer="adam", metrics=['accuracy'])
  saes.fit(X_train, y_train, batch_size=config["batch"], epochs=config["epochs"], validation_split=0.05)
  return saes

def get_tcn(input_shape):
  model = Sequential()
  model.add(TCN(128, input_shape=input_shape, kernel_size=3, dilations=[1, 2, 4, 8], return_sequences=True))
  model.add(TCN(64))
  model.add(Dropout(0.2))
  model.add(Dense(1, activation='sigmoid'))

  return model
