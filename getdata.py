import requests
import tarfile
import os

for i in range(1, 31):
    file_name = f"subwaydatanyc_2024-09-{i:02}_csv.tar.xz"
    url = f"https://subwaydata.nyc/data/{file_name}"
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(response.content)
        
        # Extract the contents of the .tar.xz file
        with tarfile.open(file_name, "r:xz") as tar:
            tar.extractall(path="./data/09-"+str(i)+"/") 
        
        # Optionally, delete the .tar.xz file after extracting if you don't need it
        os.remove(file_name)
        
        print(f"Extracted CSVs from {file_name}")
    else:
        print(f"Failed to download {file_name}")
