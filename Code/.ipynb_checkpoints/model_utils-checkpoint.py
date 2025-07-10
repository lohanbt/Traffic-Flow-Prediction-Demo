from keras.models import load_model
import csv
import joblib
import numpy as np

def get_recent_flow(scat, timesteps):
  with open("processed_data/time_series.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
      if row[0] == scat:
        return row[-timesteps:]
      



def get_next_prediction(scat, timesteps):
  flow = get_recent_flow(scat, timesteps)
  model = load_model(f"models/lstm/{scat}.h5")

  scaler = joblib.load(f'scalers/scaler_{scat}.pkl')
  
  normalized_data = scaler.transform(np.array(flow).reshape(-1, 1)).ravel().reshape(1, -1)
  pred = model.predict(normalized_data)
  scaled_pred = scaler.inverse_transform(pred.reshape(1, -1))
  return scaled_pred

