from keras.layers import Dense, LSTM, GRU, Dropout, Input
from keras.models import Sequential
from keras.models import Model
from keras import regularizers

def get_lstm(input_shape):

  model = Sequential()
  model.add(LSTM(128, input_shape=input_shape, return_sequences=True))
  model.add(LSTM(64))
  model.add(Dropout(0.2))
  model.add(Dense(1, activation='sigmoid'))

  return model

def get_gru(input_shape):
  model = Sequential()
  model.add(GRU(128, input_shape=input_shape, return_sequences=True))
  model.add(GRU(64))
  model.add(Dropout(0.2))
  model.add(Dense(1, activation='sigmoid'))

  return model

# SAE Version 2
def get_saes_v2(inputs, hidden, outputs, finalDense=False, learning_rate=1e-5):
    input_layer = Input(shape=(inputs,), name="input")
    encoder = Dense(hidden[0], activation="relu", activity_regularizer=regularizers.l1(learning_rate))(input_layer)
    encoder = Dense(hidden[1], activation="relu", activity_regularizer=regularizers.l1(learning_rate))(encoder)
    encoder = Dense(hidden[2], activation="relu", activity_regularizer=regularizers.l1(learning_rate))(encoder)

    dropouts = Dropout(0.2)(encoder)
    decoder = Dense(hidden[1], activation="relu", activity_regularizer=regularizers.l1(learning_rate))(dropouts)
    decoder = Dense(hidden[0], activation="relu", activity_regularizer=regularizers.l1(learning_rate))(decoder)
    
    if finalDense:
        decoder = Dense(1, activation="sigmoid", activity_regularizer=regularizers.l1(learning_rate))(decoder)
    else:
        decoder = Dense(outputs, activation="sigmoid", activity_regularizer=regularizers.l1(learning_rate))(decoder)
    
    autoencoder = Model(inputs=input_layer, outputs=decoder)
    return autoencoder
