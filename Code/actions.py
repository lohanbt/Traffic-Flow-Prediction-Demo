
import map_utils

# This function is called when the user clicks the "Find Path" button. It validates inputs, and call the k_shortest_paths function from map_utils.py
def find_path(graph, start, end):

  print('start finding path')
  scat = map_utils.get_scats()
  print(scat)

  print('check scat true')
  print(type(start))
  print(type(scat[0]))
  if int(start) not in scat:
    print(start)
    return "Invalid start SCAT"
  if int(end) not in scat:
    print(end)
    return "Invalid end SCAT"
  
  print("getting scatas")
  shortest_paths = map_utils.k_shortest_paths(graph, int(start), int(end), 5)
  values = {str(shortest_path[1]) : shortest_path[0] for shortest_path in shortest_paths}

  print(shortest_paths)
  return shortest_paths