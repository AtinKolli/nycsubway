import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from functions import *
import community as community_louvain
from scrape_stops import *
from statistics import mean

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


# distance to nearest station in case a certain line goes down
differences = get_differences('M', local_lines, lines, stop_mapping)
print(differences)


# load stops data with normalization
stops = {}
with open("test_stops.txt", "r") as f:
    for line in f:
        try:
            # split the line by commas
            stop_id, stop_name, stop_lat, stop_lon, _, parent_station = line.strip().split(",")
            
            # convert lat/lon to float
            stop_lat = float(stop_lat)
            stop_lon = float(stop_lon)
            
            # normalize station name and store
            normalized_name = normalize_station_name(stop_name)
            stops[normalized_name] = {
                'id': stop_id,
                'lat': stop_lat,
                'lon': stop_lon
            }
        
        except ValueError as e:
            # skip line if error
            print(f"Skipping line due to error: {e} | Line: {line.strip()}, {line.strip().split(',')}")

# checking loaded step for debugging
print("Loaded stops:", list(stops.keys())[:10])  # print first 10 station names

# get distances to nearest station in case a certain line goes down
differences = get_differences('M', local_lines, lines, stops)
print(differences)

def station_analysis():
    # parse data from data folder
    station_graph, edge_count, edge_time, visit_count, visit_time = get_data(edge_map, line_map)

    print("Station Graph:", station_graph)
    print("Edge Count:", edge_count)
    print("Edge Time:", edge_time)
    print("Visit Count:", visit_count)
    print("Visit Time:", visit_time)

    # construct graph
    G = nx.DiGraph()
    for (station1, station2) in edge_count:
        weight = edge_time[(station1, station2)] / edge_count[(station1, station2)] if edge_count[(station1, station2)] > 0 else float('inf')
        G.add_edge(station1, station2, weight=weight)

    # get global metrics
    giant_component_size_global, avg_shortest_path_len_global = calc_globals(G)

    # identify significant nodes
    components, avg_lens, significant_node_lengths = find_significant_nodes_with_lengths(G, giant_component_size_global, avg_shortest_path_len_global)

    # create dataframes for results
    component_df = pd.DataFrame(components, columns=["Impact on Giant Component Size", "Node"])
    avg_len_df = pd.DataFrame(significant_node_lengths, columns=["Impact on Average Shortest Path Length", "Node", "Length"])

    print("\nTop 10 Nodes by Impact on Giant Component Size:")
    print(component_df.head(10).to_string(index=False))

    print("\nTop 10 Nodes by Impact on Average Shortest Path Length:")
    print(avg_len_df.head(10).to_string(index=False))

    # saving tables to csv output
    component_df.to_csv("component_impact.csv", index=False)
    avg_len_df.to_csv("avg_path_length_impact.csv", index=False)

# new function to calculate lengths properly
def find_significant_nodes_with_lengths(G, giant_component_size_global, avg_shortest_path_len_global):
    components = []
    avg_lens = []
    node_lengths = []
    
    for node in list(G.nodes):
        G_removed = G.copy()
        G_removed.remove_node(node)

        # calculate giant component size after node removal
        largest_cc_size = max(len(c) for c in nx.weakly_connected_components(G_removed))
        component_impact = giant_component_size_global - largest_cc_size
        components.append((component_impact, node))

        # calculate average shortest path length after node removal
        try:
            path_lengths = dict(nx.shortest_path_length(G_removed, weight='weight'))
            avg_length = mean([length for target_lengths in path_lengths.values() for length in target_lengths.values()])
        except nx.NetworkXError:
            avg_length = float('inf')
        
        avg_impact = avg_length - avg_shortest_path_len_global
        avg_lens.append((avg_impact, node))
        node_lengths.append((avg_impact, node, avg_length))
    
    return components, avg_lens, node_lengths

station_analysis()

def plot_station_graph(station_graph):
    # create a networkx graph
    G = nx.Graph()

    # add nodes and edges
    for station1, neighbors in station_graph.items():
        for station2 in neighbors:
            G.add_edge(station1, station2)

    # draw graph
    pos = nx.spring_layout(G, seed=42)  # seed
    plt.figure(figsize=(12, 12))  # adjust the size of the plot
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray')

    plt.title("Subway Network Graph")
    plt.show()

print("Keys in stop_mapping:", list(stop_mapping.keys())[:20])  # print first 20 keys

# run station analysis to populate station_graph
station_analysis()

# check if station_graph is populated before plotting
print("Station graph contents:", station_graph)

# plot graph
if station_graph:
    plot_station_graph(station_graph)
else:
    print("Station graph is empty. Check data population.")