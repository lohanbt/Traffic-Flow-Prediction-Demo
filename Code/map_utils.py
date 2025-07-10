import math
import pandas as pd
import networkx as nx
import numpy as np
import re
import csv
import heapq
from collections import defaultdict
from model_utils import get_next_prediction

##################### Get list of SCAT Numbers #####################
def get_scats():
  df_raw = pd.read_csv("processed_data/coordinates.csv", encoding='utf-8')
  return df_raw['SCATS Number'].values.tolist()
  

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
  df = pd.read_csv("processed_data/coordinates.csv", encoding='utf-8')
  df = df[df['SCATS Number'].isin([int(scat1), int(scat2)])]

  coord1 = (df.iloc[0]['NB_LATITUDE'], df.iloc[0]['NB_LONGITUDE'])
  coord2 = (df.iloc[1]['NB_LATITUDE'], df.iloc[1]['NB_LONGITUDE'])

  print (coord1, coord2)

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

### TIME TRAVEL FORMULA BETWEEN 2 ADJACENT SCATS
def time_travel(scat1, scat2):
  distance = distance_between_two_scats(scat1, scat2)
  print("Distance",distance)

  ### Assumed kjam = 120 vehicles/km, and vmax = 60 km/h
  kjam = 120.0
  vmax = 60.0
  qmax = kjam * vmax / 4.0

  q = get_next_prediction(scat1, 12)
  print("predicted flow:", q)

  # Calculate a and b, which are the coefficients of the quadratic equation
  a = -2.0*qmax/vmax/vmax
  b = 2.0*qmax/vmax

  # Get the bigger value of the two roots
  v = max(
    ((-b - math.sqrt(b**2 + 4*a*q)) / 2/a),
    ((-b + math.sqrt(b**2 + 4*a*q)) / 2/a)
  )

  print("predicted v:",v)
  t = distance / v

  return t


# Print all intersections for testing
def print_all_intersections(map_widget, paths):
  map_widgets = {}
  with open('processed_data/coordinates.csv', mode='r') as file:
    csvreader = csv.reader(file)
    header = True
    # Loop through each row
    for row in csvreader:
      if header:
        header = False
        continue
      if int(row[0]) in paths:
        temp = map_widget.set_marker(float(row[1]), float(row[2]), text=row[0], icon=None)
        map_widgets[str(row[0])] = temp


### EXTRACT EDGES FOR GRAPH
def extract(data):
  pattern = re.compile(r"(.+)\s([SNEW]+)\s(?:[Oo][Ff])\s(.+)")
  edges = [pattern.match(entry).groups() for entry in data if pattern.match(entry)]
  return edges


### LOAD GRAPH
def build_graph(map_file):
  # Load data from csv file
  columns = ["SCATS Number", "Location", "NB_LATITUDE", "NB_LONGITUDE"]
  df = pd.read_csv("data.csv", skiprows=1, usecols=columns, encoding='utf-8').fillna(0)
  df=df.drop_duplicates()
  locations = df["Location"].tolist()
  scats = df["SCATS Number"].tolist()
  print("scat type", type(scats[0]))
  coordinates = df[["NB_LATITUDE", "NB_LONGITUDE"]].values
  coordinates = [tuple(row) for row in coordinates]
  edges = extract(locations)

  graph = defaultdict(list)

  # Get unique roads
  roads_0 = [t[0] for t in edges]
  roads_2 = [t[2] for t in edges]
  roads = roads_0 + roads_2
  roads = set(roads)

  # Initialize the roads_intersects dictionary with direction categories
  roads_intersects = {road: {direction: [] for direction in ['NS', 'WE', 'NWSE', 'SWNE']} for road in roads}

  # Fill roads_intersects with SCAT site data
  for i in range(len(edges)):
    edge = edges[i]
    road_0, road_2, direction = edge[0], edge[2], edge[1]
    coordinate = coordinates[i]
    scat = scats[i]

    if direction in ['N', 'S']:
      roads_intersects[road_0]['WE'].append((road_2, coordinate, scat))
      roads_intersects[road_2]['NS'].append((road_0, coordinate, scat))
    elif direction in ['W', 'E']:
      roads_intersects[road_0]['NS'].append((road_2, coordinate, scat))
      roads_intersects[road_2]['WE'].append((road_0, coordinate, scat))
    elif direction in ['NW', 'SE']:
      roads_intersects[road_0]['SWNE'].append((road_2, coordinate, scat))
      roads_intersects[road_2]['NWSE'].append((road_0, coordinate, scat))
    elif direction in ['NE', 'SW']:
      roads_intersects[road_0]['NWSE'].append((road_2, coordinate, scat))
      roads_intersects[road_2]['SWNE'].append((road_0, coordinate, scat))

  # Sort the SCAT sites by direction and add edges to the graph using travel time
  for road in roads_intersects:
    for direction in roads_intersects[road]:
      if len(roads_intersects[road][direction]) <= 1:
        continue  # Skip if there's no connection or only one SCAT site
      if direction == 'NS':
        roads_intersects[road][direction].sort(key=lambda x: x[1][1])  # Sort by latitude for NS roads
      else:
        roads_intersects[road][direction].sort(key=lambda x: x[1][0])  # Sort by longitude for WE roads

      # Add edges between consecutive SCAT sites with travel time as the edge weight
      for i in range(len(roads_intersects[road][direction]) - 1):
        scat1, scat2 = roads_intersects[road][direction][i][2], roads_intersects[road][direction][i+1][2]
        coord1, coord2 = roads_intersects[road][direction][i][1], roads_intersects[road][direction][i+1][1]
        # **Avoid adding edges between the same SCAT site**
        if scat1 != scat2:  # Ensure they are not the same SCAT site
          time = time_travel(scat1, scat2)  # Calculate travel time
          graph[scat1].append((scat2, time))
          graph[scat2].append((scat1, time))  # Add reverse direction as it's undirected

  return graph

# Return the K shortest paths between two nodes in a graph
def k_shortest_paths(graph, start, end, K):
  # Priority queue to store paths (total_travel_time, path)
  heap = []
  heapq.heappush(heap, (0, [start]))  # (total_travel_time, path)
  
  # List to store the K shortest paths found
  shortest_paths = []

  # Set to keep track of visited paths to avoid revisiting the same path
  visited_paths = set()

  counter = 0
  while heap and len(shortest_paths) < K:
    total_time, path = heapq.heappop(heap)
    current_node = path[-1] # Accesses the last element in the path

    # If the last node is the destination, add the path to the shortest_paths list
    if current_node == end:
      path_tuple = tuple(path)
      if path_tuple not in visited_paths:
        shortest_paths.append((total_time, path))
        visited_paths.add(path_tuple)
      continue

    # Explore neighbors
    for neighbor, travel_time in graph.get(current_node, []):
      if neighbor not in path:  # Avoid cycles
        new_total_time = total_time + travel_time
        new_path = path + [neighbor]
        heapq.heappush(heap, (new_total_time, new_path))

    counter += 1
    print("still finding", counter)

  print("final counter", counter)
  result = []
  for shortest_path in shortest_paths:
    result.append((hour_to_minutes(shortest_path[0]), shortest_path[1]))
  return result


# Convert hours to minutes
def hour_to_minutes(time):
  
  minutes = round(time * 60, 2)
  return minutes

# Print the path on the map UI
def print_path(map_widget, path):
  map_widgets = {}
  with open('processed_data/coordinates.csv', mode='r') as file:
    csvreader = csv.reader(file)
    header = True
    # Loop through each row
    for row in csvreader:
      if header:
        header = False
        continue
      if int(row[0]) in path:
        temp = map_widget.set_marker(float(row[1]), float(row[2]), text=row[0], icon=None)
        map_widgets[row[0]] = temp

  print(map_widgets.keys())
  for i in range(len(path) - 1):
    scat1, scat2 = path[i], path[i+1]
    map_widget.set_path([map_widgets[str(scat1)].position, map_widgets[str(scat2)].position])