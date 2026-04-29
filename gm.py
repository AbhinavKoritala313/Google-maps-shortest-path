import folium
import osrm
from geopy.geocoders import ArcGIS
import math
from collections import defaultdict

# Initialize geocoder and list for locations
arc = ArcGIS()
locs = []

# Input number of locations (max 9)
n = int(input("Enter number of locations (up to 9): "))

if n > 9:
    print("Please enter a number of locations from 1 to 9.")
    exit()

# Get locations and their coordinates
for i in range(n):
    enter = input(f"Enter location {i + 1}: ")
    location = arc.geocode(enter)
    if location:
        print(f"Location found: {enter}")
        print(f"Latitude: {location.latitude}, Longitude: {location.longitude}")
        locs.append([float(location.latitude), float(location.longitude)])
    else:
        print(f"Location not found for: {enter}")

# Function to compute distance between two locations
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # Radius of Earth in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

# Graph class to represent the network of locations
class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances[(to_node, from_node)] = distance

# Dijkstra's algorithm to find the shortest path
def dijkstra(graph, initial, destination):
    visited = {initial: 0}
    nodes = set(graph.nodes)
    li = []

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break
        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            weight = current_weight + graph.distances[(min_node, edge)]
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                li.append(min_node)

    root = []
    for i in li:
        if i not in root:
            root.append(i)

    return visited.get(destination, float('inf')), root  # Return infinity if destination is not reachable

# Initialize the graph with the locations
p = Graph()
for i in range(n):
    p.add_node(i)

# Add edges between locations dynamically
for i in range(n):
    for j in range(i + 1, n):
        dist = int(distance(locs[i], locs[j]) * 1000)  # Distance in meters
        p.add_edge(i, j, dist)

# Input source and destination nodes
source = int(input(f"Enter source node (0-{n-1}): "))  # Nodes range from 0 to n-1
dest = int(input(f"Enter destination node (0-{n-1}): "))

# Get the shortest path using Dijkstra's algorithm
shortest_distance, shortest_path = dijkstra(p, source, dest)

# Print the shortest path and total distance
if shortest_distance == float('inf'):
    print(f"No path found from {source} to {dest}.")
else:
    print(f"Shortest path from {source} to {dest} is {shortest_path} with a total distance of {shortest_distance / 1000} km.")

# Map visualization
map = folium.Map(location=locs[0], zoom_start=7)

# Add markers for each location
for i in range(n):
    folium.Marker(location=locs[i], popup=f"Location {i+1}").add_to(map)

# Get the driving routes from OSRM for the shortest path
if shortest_path:  # Ensure the shortest path is not empty
    path_coords = []
    for i in range(len(shortest_path) - 1):
        # Get route between two locations using OSRM API
        route = osrm.simple_route(
            locs[shortest_path[i]][::-1], locs[shortest_path[i + 1]][::-1]
        )
        for step in route['routes'][0]['geometry']['coordinates']:
            path_coords.append([step[1], step[0]])  # Reverse to Lat, Lon for folium

    # Add the driving route to the map (blue line)
    folium.PolyLine(path_coords, color='blue', weight=5, opacity=0.7).add_to(map)

# Add lines for all connections (grey)
for i in range(n):
    for j in range(i + 1, n):
        path_coords = [locs[i], locs[j]]
        folium.PolyLine(path_coords, color='grey', weight=2, opacity=0.5).add_to(map)

# Save the map to an HTML file
map.save("shortest_path_map_with_road.html")
