import pandas
import networkx as nx
import bisect
import random
from functions import *
import community as community_louvain
from scrape_stops import *


visit_count={}
visit_time={}
edge_count={}
edge_time={}
station_graph={}

edge_map, line_map, lines = get_lines()
# rails = {"Broadway": {'N',"Q",'R','W'}, "7 Ave": {"1", '2', '3'}, "Lexington Ave": {"4", '5', '6'}, "8 Ave": {"A", 'C', 'E'}, "6 Ave": {"B", 'F', 'M'}, "Queens Blvd": {'M', 'R'}}
# express_lines = {"A",'B','D','N','Q','4','5'}
local_lines = {'C': {'A'}, 'E': {"F", 'M', 'A'}, 'F':{'E', 'B'}, 'M': {'R', 'F', 'J'}, 'R': {'M', 'W', 'N'}, 'W':{'N', 'Q', 'R'}, '1': {'2', '3'}, '6': {'4', '5'}}

#gets distances to nearest station in case a certain line goes down. for now, the distance method returns a placeholder value of 10
differences = get_differences('M', local_lines, lines)
print(differences)

#stuff from project checkup. not working on it rn, but can keep it for later
def station_analysis():
    # parse data from data folder
    station_graph, edge_count, edge_time, visit_count, visit_time = get_data(edge_map, line_map)

    print(station_graph, edge_count, edge_time, visit_count, visit_time)

    #construct graph
    G = nx.DiGraph() 
    for (station1, station2) in edge_count:
        G.add_edge(station1, station2, weight = edge_time[(station1, station2)]/edge_count[(station1, station2)])

    #get biggest component, average shortest path, and efficiency
    giant_component_size_global, avg_shortest_path_len_global = calc_globals(G)

    components, avg_lens, efficiencies = find_significant_nodes(G, giant_component_size_global, avg_shortest_path_len_global)

    print("Most significant by giant component size", components[:20])
    print("Most significant by avg shortest path", avg_lens[:20])

    find_communities(G)

