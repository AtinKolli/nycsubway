import pandas
import networkx as nx
import bisect
import random
from functions import *
import community as community_louvain

stop_mapping={}
with open("stops.txt", "r") as f:
    for line in f:
        info=line.split(",")
        stop_mapping[info[0]]=info[1]

visit_count={}
visit_time={}
edge_count={}
edge_time={}
station_graph={}

#parse data from data folder
get_data(station_graph, edge_count, edge_time, visit_count, visit_time)

print(station_graph, edge_count, edge_time, visit_count, visit_time)

#construct graph
G = nx.DiGraph() 
for (station1, station2), trip_count in edge_count.items():
    G.add_edge(station1, station2, weight=trip_count)

#get biggest component, average shortest path, and efficiency
giant_component_size_global, avg_shortest_path_len_global, efficiency_global = calc_globals(G)

components, avg_lens, efficiencies = find_significant_nodes(G, giant_component_size_global, avg_shortest_path_len_global, efficiency_global)

print("Most significant by giant component size", components[:20])
print("Most significant by avg shortest path", avg_lens[:20])
print("Most significant by efficiency", efficiencies[:20])
