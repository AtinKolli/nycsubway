import pandas
import networkx as nx
import bisect

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

for i in range(1, 31):
    folder="data/09-"+str(i)+"/"
    filename=folder+"subwaydatanyc_2024-09-"+str(i)+"_stop_times.csv"
    if i<10:
        filename=folder+"subwaydatanyc_2024-09-0"+str(i)+"_stop_times.csv"
    df=pandas.read_csv(filename)
    current_trips={}
    for index, row in df.iterrows():
        if row['trip_uid'] not in current_trips or row['arrival_time']-current_trips[row['trip_uid']][1]<20:
            current_trips[row['trip_uid']]=[row['stop_id'], row['departure_time']]
        else:
            prev_stop,prev_time=current_trips[row['trip_uid']]
            if row['arrival_time']-current_trips[row['trip_uid']][1]<20:
                print(index,i)
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
    print("finished",i)


average_visits=[]
average_edge=[]

for stop in visit_count:
    average_visits.append([visit_time[stop]/visit_count[stop],stop])
for edge in edge_count:
    average_edge.append([edge_time[edge]/edge_count[edge],edge])
    station_graph[edge[0]].append([edge[1],edge_time[edge]/edge_count[edge]])

G = nx.DiGraph()  # Directed graph as it's a subway network with directed travel
for node, neighbors in station_graph.items():
    for neighbor, travel_time in neighbors:
        if travel_time<20:
            print(node,neighbor,travel_time,edge_time[(node,neighbor)]/edge_count[(node,neighbor)])
        G.add_edge(node, neighbor, weight=travel_time)

for u, v, data in G.edges(data=True):
    if data['weight'] <= 0:
        print(f"Edge ({u}, {v}) has non-positive weight: {data['weight']}")
print(len(G.edges(data=True)))

# 1. Giant Component Size (strongly connected for directed graph)
largest_cc = max(nx.strongly_connected_components(G), key=len)
giant_component_size = len(largest_cc)
print("Giant Component Size:", giant_component_size)

# 2. Average Shortest Path Length (only for the largest strongly connected component)
subgraph = G.subgraph(largest_cc).to_undirected()
try:
    avg_shortest_path_len = nx.average_shortest_path_length(subgraph, weight='weight', method='bellman-ford')
    print("Average Shortest Path Length (Bellman-Ford):", avg_shortest_path_len)
except nx.NetworkXError as e:
    print("Error calculating shortest path length:", e)

# 3. Network Efficiency
efficiency = nx.global_efficiency(subgraph)
print("Network Efficiency:", efficiency)

# 4. Betweenness Centrality
node_betweenness = nx.betweenness_centrality(G, weight='weight')
edge_betweenness = nx.edge_betweenness_centrality(G, weight='weight')

# Print node and edge betweenness
print("Node Betweenness Centrality (Top 5):", sorted(node_betweenness.items(), key=lambda x: x[1], reverse=True)[:5])
print("Edge Betweenness Centrality (Top 5):", sorted(edge_betweenness.items(), key=lambda x: x[1], reverse=True)[:5])

average_visits.sort()
average_edge.sort()
average_visits.reverse()
average_edge.reverse()