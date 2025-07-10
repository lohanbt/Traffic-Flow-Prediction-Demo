import math
import pandas as pd
import networkx as nx
from model_utils import get_next_prediction

##################### Calculate the distance between two coordinates (lat, long) #####################
def distance_between_two_coordinates(coord1, coord2):
  # Unpack coordinates
  lat1, lon1 = coord1
  lat2, lon2 = coord2
  
  # Convert latitude and longitude from degrees to radians
  lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
  
  # Haversine formula
  dlat = lat2 - lat1
  dlon = lon2 - lon1
  a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
  c = 2 * math.asin(math.sqrt(a))
  
  # Radius of Earth in kilometers (use 3956 for miles)
  r = 6371.0
  
  # Calculate the distance
  distance = c * r
  return distance
  
### CALCULATE DISTANCE BETWEEN 2 SCATS
def distance_between_two_scats(scat1, scat2):
  df = pd.read_csv("map/coordinates_fixed.csv", encoding='utf-8')
  df = df[df['SCATS_Number'].isin([int(scat1), int(scat2)])]

  coord1 = (df.iloc[0]['NB_LATITUDE'], df.iloc[0]['NB_LONGITUDE'])
  coord2 = (df.iloc[1]['NB_LATITUDE'], df.iloc[1]['NB_LONGITUDE'])

  return distance_between_two_coordinates(coord1, coord2)


### FIND PATH BETWEEN 2 SCATS
def find_scat_path(map_file, start, end):
  G = nx.read_gml(map_file)

  startNode = None
  endNode = None

  for node in G.nodes:
    if node == start:
      startNode = node
    if node == end:
      endNode = node

  if (not startNode or not endNode):
    return None
  paths = nx.all_shortest_paths(G, startNode, endNode, weight="weights")

  scat_list = [p for p in paths]

  return scat_list
  cost = 0
  for i in range(len(path) - 1):
    cost += G[path[i]][path[i+1]]['weight']
  return ([G.nodes[node].get('label') for node in path], cost)

def time_travel(scat1, scat2):
  distance = distance_between_two_scats(scat1, scat2)
  print("Distance",distance)
  kjam = 120.0
  vmax = 60.0
  qmax = kjam * vmax / 4.0

  q = get_next_prediction(scat1, 12)
  print("predicted flow:", q)

  a = -4.0*qmax/vmax/vmax
  b = 4.0*qmax/vmax

  v = max(
    ((-b - math.sqrt(b**2 + 4*a*q)) / 2/a),
    ((-b + math.sqrt(b**2 + 4*a*q)) / 2/a)
  )

  print("predicted v:",v)
  t = distance / v

  return t