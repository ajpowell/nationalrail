import json
import os
import re
import sys

path = './data/2025/01/16'
# file = '162748-NCL.json'

latest_services = []

# Need to sort filenames or returned in random order
# Sorting by filename...
file_list = sorted(os.scandir(path),key=lambda e: e.name)

# Iterate over all files in the directory
for entry in file_list:
    print(f'..got {entry.name}..')
    if entry.is_file() and not re.search('^\..*', entry.name):
        file = entry.name
        # if file == '.DS_Store':
        #     break
        print(f'Processing {file}')

        # For each file, read contents and 
        with open(path + '/' + file, 'r') as fh:
            rawdata = fh.read()
            services = json.loads(rawdata)

            for service in services:
                print('{} -  {} {} {} (arr:{}) -> {} (dep:{})'.format(file, service["id"], service["operatorCode"], service["origin"], service["sched_arr"], service["destination"], service["sched_dep"]))
                service_added = False
                for latest in latest_services:
                    if latest["id"] == service["id"] and not service_added:
                        # Remove the old record and add the new one
                        latest_services.remove(latest)
                        # Retain the first file details
                        service["meta_first_file"] = latest["meta_first_file"]
                        # Add this latest file
                        service["meta_last_file"] = path + '/' + file
                        latest_services.append(service)
                        service_added = True
                        print('Replaced...')
                # Add if this is first time we have seen this service
                if not service_added:
                    service["meta_first_file"] = path + '/' + file
                    latest_services.append(service)
                    print('Added...')
                
print('===========================================')

for service in latest_services:
    # print(service)
    # Attempt to pull out last file - may not be present if only seen once
    try:
        lastfile = service["meta_last_file"]
    except:
        lastfile = ''
    
    print('{} ({}) -> {} {} {} (arr:{}) -> {} (dep:{})'.format(service["meta_first_file"], lastfile, service["id"], service["operatorCode"], service["origin"], service["sched_arr"], service["destination"], service["sched_dep"]))
