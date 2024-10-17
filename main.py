import pandas
stop_mapping={}
with open("stops.txt", "r") as f:
    for line in f:
        info=line.split(",")
        stop_mapping[info[0]]=info[1]

visit_count={}
visit_time={}

edge_count={}
edge_time={}

for i in range(1, 31):
    folder="data/09-"+str(i)+"/"
    filename=folder+"subwaydatanyc_2024-09-"+str(i)+"_stop_times.csv"
    if i<10:
        filename=folder+"subwaydatanyc_2024-09-0"+str(i)+"_stop_times.csv"
    df=pandas.read_csv(filename)
    current_trips={}
    for index, row in df.iterrows():
        if row['trip_uid'] not in current_trips:
            current_trips[row['trip_uid']]=[row['stop_id'], row['departure_time']]
        else:
            prev_stop,prev_time=current_trips[row['trip_uid']]
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

average_visits.sort()
average_edge.sort()
average_visits.reverse()
average_edge.reverse()


