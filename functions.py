import pandas
import networkx as nx
import bisect
import random
import community as community_louvain
from collections import defaultdict


def get_data(station_graph, edge_count, edge_time, visit_count, visit_time):
    for i in range(1, 31):
        folder="data/09-"+str(i)+"/"
        filename=folder+"subwaydatanyc_2024-09-"+str(i)+"_stop_times.csv"
        if i<10:
            filename=folder+"subwaydatanyc_2024-09-0"+str(i)+"_stop_times.csv"
        df=pandas.read_csv(filename)
        current_trips={}
        for index, row in df.iterrows():
            #Second condition handles errors in data where arrival time is too early. In this case, treat it as new trip
            if row['trip_uid'] not in current_trips or row['arrival_time']-current_trips[row['trip_uid']][1]<20:
                current_trips[row['trip_uid']]=[row['stop_id'], row['departure_time']]
            else:
                prev_stop,prev_time=current_trips[row['trip_uid']]
                if prev_stop not in station_graph:
                    station_graph[prev_stop]=[]
                edge=(prev_stop,row["stop_id"])
                if edge not in edge_count:
                    edge_count[edge]=0
                    edge_time[edge]=0
                edge_count[edge]+=1
                edge_time[edge]+=row['arrival_time']-prev_time
                if pandas.isna(row['departure_time']) or row['departure_time'] == '': continue
                if row['stop_id'] not in visit_count:
                    visit_count[row["stop_id"]]=0
                    visit_time[row["stop_id"]]=0
                visit_count[row["stop_id"]]+=1
                visit_time[row["stop_id"]]+=row["departure_time"]-row['arrival_time']
                current_trips[row['trip_uid']]=[row['stop_id'], row['departure_time']]
        print("got data for day",i)

def calc_globals(G):
    largest_cc_global = max(nx.strongly_connected_components(G), key=len)
    giant_component_size_global = len(largest_cc_global)
    print("Giant Component Size:", giant_component_size_global)

    subgraph_global = G.subgraph(largest_cc_global).to_undirected()
    try:
        avg_shortest_path_len_global = nx.average_shortest_path_length(subgraph_global, weight='weight', method='bellman-ford')
        print("Average Shortest Path Length (Bellman-Ford):", avg_shortest_path_len_global)
    except nx.NetworkXError as e:
        print("Error calculating shortest path length:", e)

    efficiency_global = nx.global_efficiency(subgraph_global)
    print("Network Efficiency:", efficiency_global)

    return [giant_component_size_global, avg_shortest_path_len_global, efficiency_global]

#iterate through every node and calculate network robustness measures with it removed
def find_significant_nodes(G, giant_component_size_global, avg_shortest_path_len_global, efficiency_global):
    nodes = list(G.nodes())
    components=[]
    avg_lens=[]
    efficiencies=[]
    count=0
    for node_to_remove in G:
        component_size, avg_len, efficiency = simulate_node_failure(G,node_to_remove)
        components.append([giant_component_size_global-component_size,node_to_remove])
        avg_lens.append([avg_shortest_path_len_global-avg_len, node_to_remove])
        efficiencies.append([efficiency_global-efficiency, node_to_remove])
        count+=1
    
    components=sorted(components)[::-1]
    avg_lens=sorted(avg_lens)[::-1]
    efficiencies=sorted(efficiencies)[::-1]

    return [components, avg_lens, efficiencies]

#helper method. remove node and calculate robustness
def simulate_node_failure(G,node_to_remove):
    G_copy = G.copy()
    
    G_copy.remove_node(node_to_remove)
    print(f"Removed node: {node_to_remove}")
    
    largest_cc = max(nx.strongly_connected_components(G_copy), key=len)
    giant_component_size = len(largest_cc)
    undirected_subgraph = G_copy.subgraph(largest_cc).to_undirected()
    avg_shortest_path_len = nx.average_shortest_path_length(undirected_subgraph, weight='weight', method='bellman-ford')
    efficiency = nx.global_efficiency(undirected_subgraph)
    
    return [giant_component_size,avg_shortest_path_len, efficiency]

def find_communities(G):
    G_undirected = G.to_undirected()
    partition = community_louvain.best_partition(G_undirected, weight='weight')
    communities = defaultdict(list)
    for node, community_id in partition.items():
        communities[community_id].append(node)

    print("Detected Communities:")
    for community_id, nodes in communities.items():
        print(f"Community {community_id}: {nodes}")