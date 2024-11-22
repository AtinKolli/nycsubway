from bs4 import BeautifulSoup
import requests
import pickle

def get_lines():
    line_names = [str(x) for x in range(1, 8)] + [x for x in "ABCDEFGJLMNQRSWZ"]
    #maps lines to edges
    edge_map = {}
    #maps edges to lines
    line_map = {}
    #lines to stations
    lines = {}
    for line in line_names:
        edge_map[line]=set()
        lines[line] = []
        # URL of the webpage
        url = "https://new.mta.info/maps/subway-line-maps/" + line + "-line"  # Replace with your target URL

        print(url)

        # Send a GET request to fetch the raw HTML content
        response = requests.get(url)

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        stops = []

        tables = soup.find_all('tbody')

        for table in tables:
            table_rows = table.find_all('tr')
            for row in table_rows:
                stops.append(row.find("td").find("p").text.strip())

        for x in range(len(stops)-1):
            e1=(stops[x], stops[x+1])
            edge_map[line].add(e1)
            if e1 not in line_map:
                line_map[e1] = set()
            line_map[e1].add(line)
            lines[line].append(stops[x])
        lines[line].append(stops[-1])
        for x in range(len(stops)-1):
            e1=(stops[-(x+1)],stops[-(x+2)])
            edge_map[line].add(e1)
            if e1 not in line_map:
                line_map[e1] = set()
            line_map[e1].add(line)
        
    return edge_map, line_map, lines
        
        # print(line, stops)


        # # Pickle the object and save it to a file
        # with open('./lines/line'+line+'.pkl', 'wb') as file:  # 'wb' mode for writing binary
        #     pickle.dump(stops, file)

        # print("Object pickled and saved to data.pkl")

