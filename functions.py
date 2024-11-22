import pandas
import networkx as nx
import bisect
import random
import community as community_louvain
from collections import defaultdict

#read lines.txt and return a dictionary that maps each stop to the lines it serves
def read_stops():
    stop_lines = {}
    with open("lines.txt", "r") as f:
        for line in f:
            info=line.split(",")
            stop_name = info[5]
            if stop_name not in stop_lines:
                stop_lines[stop_name] = []
            lines = info[8].split(' ')
            stop_lines[stop_name].append(lines)
    return stop_lines

#given a stop name and two lines, check if they are referring to the same station. there are some stations with the same name but different locations
#this method confirms if they refer to the same station. might be useful in distance function
def verify_match(stop, line_name1, line_name2, stop_lines):
    if stop not in stop_lines:
        return True
    for lines in stop_lines[stop]:
        if line_name1 in lines and line_name2 not in lines or line_name1 not in lines and line_name2 in lines:
            return False
    return True

#helper for find_merged_segments
def find_segments(line_name1, line_name2, line1, line2):
    stop_lines = read_stops()
    stops1=set(line1)
    start=0
    while start<len(line2) and not (line2[start] in stops1 and verify_match(line2[start], line_name1, line_name2, stop_lines)):
        start+=1
    segments=[]
    current_segment = []
    for i2 in range(start, len(line2)):
        stop = line2[i2]
        if stop not in stops1 or not verify_match(line2[i2], line_name1, line_name2, stop_lines):
            if not current_segment: continue
            if len(current_segment) > 1:
                segments.append(current_segment)
            current_segment = []
        else:
            current_segment.append(stop)
    if len(current_segment) > 1:
        segments.append(current_segment)
    return segments

#find segments of the paths to see where they run together. line 1 is local, and line 2 is express or local. checks reverse ordering too
def get_merged_segments(line_name1, line_name2, lines):
    line1, line2 = lines[line_name1], lines[line_name2]
    line2_reversed = line2[::-1]
    segments, reversed_segments = find_segments(line_name1, line_name2, line1, line2), find_segments(line_name1, line_name2, line1, line2_reversed)
    return segments, reversed_segments

#use latitude longitude or some other API or method to find distance between two stops. add parameters if necessary
def find_distance(place1, place2):
    #TODO
    return 10

#helper to find differences for each stop on the line to nearest stop served by an overlapping line
def find_differences(line_name, alternate_name, lines_list, stop_lines, segments):
    line = lines_list[line_name]
    differences={stop: float('inf') for stop in line}
    alternate_line = lines_list[alternate_name]
    if not segments: 
        return None
    cur_segment = 0
    segment_index = 0
    i=0
    while i<len(line) and (line[i] != segments[0][0] or not verify_match(line[i], line_name, alternate_name, stop_lines)):
        i+=1
    while i < len(line):
        stop = line[i]
        if cur_segment == len(segments): 
            i+=1
            continue
        if stop == segments[cur_segment][segment_index] and verify_match(stop, line_name, alternate_name, stop_lines):
            # if segment_index == 0 and i > 0:
            #     differences[line[i-1]]=min(differences[line[i-1]], find_distance(line[i-1], segments[cur_segment][0]))
            differences[stop] = 0
            segment_index += 1
            if segment_index == len(segments[cur_segment]):
                # if i<len(line)-1:
                #     differences[line[i+1]] = min(differences[line[i+1]], find_distance(line[i+1], segments[cur_segment][-1]))
                cur_segment += 1
                segment_index = 0
        else:
            differences[stop] = find_distance(stop, segments[cur_segment][segment_index])
            if segment_index > 0:
                differences[stop] = min(differences[stop], find_distance(stop, segments[cur_segment][segment_index - 1]))
            elif cur_segment > 0:
                differences[stop] = min(differences[stop], find_distance(stop, segments[cur_segment - 1][-1]))
        i+=1
    # print(alternate_name, differences)
    return differences

# for each stop on the line, get the distance to the nearest stop that is served by a different line(0 if other line serves same station). used to simulate if line goes down
#TODO: if a stop is further than a certain value(lets say 0.3 miles), set distance to infinity to say it is unreachable
#Could also change it so that if a station is >=x stops away from the nearest shared segment, it is set to unreachable. would have to change find_differences for that
def get_differences(line_name, local_lines, lines_list):
    stop_lines = read_stops()
    line = lines_list[line_name]
    differences={stop: [float('inf'), None] for stop in line}
    for alternate_name in local_lines[line_name]:
        alternate_line = lines_list[alternate_name]
        segments, reversed_segments = get_merged_segments(line_name, alternate_name, lines_list)
        new_differences = find_differences(line_name, alternate_name, lines_list, stop_lines, segments)
        reversed_differences = find_differences(line_name, alternate_name, lines_list, stop_lines, reversed_segments)
        for stop in new_differences:
            if new_differences[stop] < differences[stop][0]:
                differences[stop] = (new_differences[stop], alternate_name)
        for stop in reversed_differences:
            if reversed_differences[stop] < differences[stop][0]:
                differences[stop] = (reversed_differences[stop], alternate_name)
    return differences




def get_data(edge_map, line_map):
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
    # current_lines = {}

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
                current_trips[row['trip_uid']]=[stop_mapping[row['stop_id']], row['departure_time']]
                # current_lines[row['trip_uid']]={line for line in line_map}
            else:
                prev_stop,prev_time=current_trips[row['trip_uid']]
                if prev_stop not in station_graph:
                    station_graph[prev_stop]=[]
                edge=(prev_stop, stop_mapping[row["stop_id"]])
                # current_lines[row['trip_uid']] = line_map[edge] & current_lines[row['trip_uid']]
                if edge not in edge_count:
                    edge_count[edge]=0
                    edge_time[edge]=0
                edge_count[edge]+=1
                edge_time[edge]+=row['arrival_time']-prev_time
                if pandas.isna(row['departure_time']) or row['departure_time'] == '': continue
                if stop_mapping[row["stop_id"]] not in visit_count:
                    visit_count[stop_mapping[row["stop_id"]]]=0
                    visit_time[stop_mapping[row["stop_id"]]]=0
                visit_count[stop_mapping[row["stop_id"]]]+=1
                visit_time[stop_mapping[row["stop_id"]]]+=row["departure_time"]-row['arrival_time']
                current_trips[row['trip_uid']]=[stop_mapping[row["stop_id"]], row['departure_time']]
        print("got data for day",i)
    return station_graph, edge_count, edge_time, visit_count, visit_time

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

    return [giant_component_size_global, avg_shortest_path_len_global]

#iterate through every node and calculate network robustness measures with it removed
def find_significant_nodes(G, giant_component_size_global, avg_shortest_path_len_global):
    nodes = list(G.nodes())
    components=[]
    avg_lens=[]
    count=0
    for node_to_remove in G:
        component_size, avg_len = simulate_node_failure(G,node_to_remove)
        components.append([giant_component_size_global-component_size,node_to_remove])
        avg_lens.append([avg_shortest_path_len_global-avg_len, node_to_remove])
        count+=1
    
    components=sorted(components)[::-1]
    avg_lens=sorted(avg_lens)[::-1]
    return [components, avg_lens]

#helper method. remove node and calculate robustness
def simulate_node_failure(G,node_to_remove):
    G_copy = G.copy()
    
    G_copy.remove_node(node_to_remove)
    print(f"Removed node: {node_to_remove}")
    
    largest_cc = max(nx.strongly_connected_components(G_copy), key=len)
    giant_component_size = len(largest_cc)
    undirected_subgraph = G_copy.subgraph(largest_cc).to_undirected()
    avg_shortest_path_len = nx.average_shortest_path_length(undirected_subgraph, weight='weight', method='bellman-ford')
    
    return [giant_component_size,avg_shortest_path_len]

def find_communities(G):
    G_undirected = G.to_undirected()
    partition = community_louvain.best_partition(G_undirected, weight='weight')
    communities = defaultdict(list)
    for node, community_id in partition.items():
        communities[community_id].append(node)

    print("Detected Communities:")
    for community_id, nodes in communities.items():
        print(f"Community {community_id}: {nodes}")