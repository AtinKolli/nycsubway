import pandas
import networkx as nx
import bisect
import random
from functions import *
import community as community_louvain
from scrape_stops import *

visit_count = {}
visit_time = {}
edge_count = {}
edge_time = {}
station_graph = {}

edge_map, line_map, lines = get_lines()

local_lines = {
    'C': {'A'},
    'E': {"F", 'M', 'A'},
    'F': {'E', 'B'},
    'M': {'R', 'F', 'J'},
    'R': {'M', 'W', 'N'},
    'W': {'N', 'Q', 'R'},
    '1': {'2', '3'},
    '6': {'4', '5'}
}

stop_mapping = read_stop_mapping()


# Gets distances to nearest station in case a certain line goes down.
differences = get_differences('M', local_lines, lines, stop_mapping)
print(differences)

# Load stops data with normalization and error handling
stops = {}
with open("test_stops.txt", "r") as f:
    for line in f:
        try:
            # Split the line by commas
            stop_id, stop_name, stop_lat, stop_lon, _, parent_station = line.strip().split(",")
            
            # Attempt to convert lat/lon to float
            stop_lat = float(stop_lat)
            stop_lon = float(stop_lon)
            
            # Normalize station name and store the data
            normalized_name = normalize_station_name(stop_name)
            stops[normalized_name] = {
                'id': stop_id,
                'lat': stop_lat,
                'lon': stop_lon
            }
        
        except ValueError as e:
            # Print error message and skip the line if there's a problem with conversion
            print(f"Skipping line due to error: {e} | Line: {line.strip()}")

# Debugging: Check loaded stops
print("Loaded stops:", list(stops.keys())[:10])  # Print first 10 normalized station names

# Get distances to nearest station in case a certain line goes down
differences = get_differences('M', local_lines, lines, stops)
print(differences)

# Station analysis function
def station_analysis():
    # Parse data from data folder
    station_graph, edge_count, edge_time, visit_count, visit_time = get_data(edge_map, line_map)

    print(station_graph, edge_count, edge_time, visit_count, visit_time)

    # Construct graph
    G = nx.DiGraph()
    for (station1, station2) in edge_count:
        G.add_edge(station1, station2, weight=edge_time[(station1, station2)] / edge_count[(station1, station2)])

    # Get biggest component, average shortest path, and efficiency
    giant_component_size_global, avg_shortest_path_len_global = calc_globals(G)

    components, avg_lens, efficiencies = find_significant_nodes(
        G, giant_component_size_global, avg_shortest_path_len_global
    )

    print("Most significant by giant component size", components[:20])
    print("Most significant by avg shortest path", avg_lens[:20])

    find_communities(G)
