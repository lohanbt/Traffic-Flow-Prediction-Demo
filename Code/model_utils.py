from keras.models import load_model
import csv
import joblib
import numpy as np

# Load the recent flow data from static csv file
def get_recent_flow(scat, timesteps):
  with open("processed_data/time_series.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
      if int(row[0]) == int(scat):
        print(row[-timesteps:])
        return row[-timesteps:]
      


# Load the data, the model, and get the prediction at next time step
def get_next_prediction(scat, timesteps):
  flow = get_recent_flow(scat, timesteps)
  model = load_model(f"models/v1/lstm/{scat}.h5")

  scaler = joblib.load(f'scalers/scaler_{scat}.pkl')
  
  normalized_data = scaler.transform(np.array(flow).reshape(-1, 1)).ravel().reshape(1, -1)
  print("normalized_data", normalized_data)
  pred = model.predict(normalized_data)
  print("pred", pred)
  scaled_pred = scaler.inverse_transform(pred.reshape(1, -1))

  print("scaled_pred", scaled_pred)
  return scaled_pred

