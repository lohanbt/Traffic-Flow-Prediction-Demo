# Traffic Flow Prediction Demo
 My contributions to this project:
 1. Training both v1 and v2 models for lstm, gru, and saesv2
 2. Constructing and visualising node graph of SCAT sites along with the implementation of breadth first search:

 We begin by extracting location details from our dataset using regular expressions to identify key elements, such as roads and travel directions. We then create a graph structure where each SCAT site is a node, and the connections between them represent roads with travel times as edge weights. The travel time between two SCAT sites is calculated using a custom function called time_travel. This function takes into account predicted traffic flow and speed based on the distance between the sites. essentially, it ensures that travel times are calculated realistically based on the current conditions at each SCAT site.

 Now, for pathfinding, we use Dijkstra's algorithm. It’s an efficient choice because it finds the shortest path in graphs with non-negative weights and is relatively simple to implement. While there are more complex algorithms like Yen's Algorithm to find multiple paths, we extended Dijkstra to find the top 5 shortest paths, which strikes a good balance between performance and complexity. This extension avoids unnecessary computational overhead while still delivering accurate results. Essentially, it ensures that travel times are calculated realistically based on the current conditions at each SCAT site.
 
 For pathfinding, we use Dijkstra's algorithm. It’s an efficient choice because it finds the shortest path in graphs with non-negative weights and is relatively simple to implement. While there are more complex algorithms like Yen's Algorithm to find multiple paths, we extended Dijkstra to find the top 5 shortest paths, which strikes a good balance between performance and complexity. This extension avoids unnecessary computational overhead while still delivering accurate results.
