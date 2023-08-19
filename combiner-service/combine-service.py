from flask import Flask
from flask_cors import CORS
import requests
import json

# Open File Containing the Addresses to GET
file_path = 'addresses.txt'
urls = []

try:
    with open(file_path, 'r') as file:
        for line in file:
            ip = line.strip()
            urls.append(ip)
except FileNotFoundError:
    print(f"File '{file_path}' not found.")

print("IP addresses read from the file:", urls)

app = Flask(__name__)
CORS(app)

#@app.route('/ads-b-combined')
@app.route('/combined_get')
def combined_get():
    report_time = 0
    elapsed_time = 0
    states = []
    all_states = ""

    for url in urls:
        try:
            response = requests.get(url)
        except:
            print("No data from " + url)
        else:
            data_json = json.loads(response.text)
            report_time = data_json['report_time']
            elapsed_time += data_json['elapsed_time_us']
            states = str(data_json['states']).replace('[', '').replace(']', '').replace('\'', '\"')
            all_states += states
            print(states)

    report_time = str(report_time)
    elapsed_time = str(elapsed_time)
    all_states = all_states.replace('}{', '},{')
    print(all_states)
    new_message = '{"report_time":' + report_time + ',"elapsed_time_us":' + elapsed_time + ',"states":[' + all_states + ']}'
    new_data = json.loads(new_message)

    return new_data

if __name__ == '__main__':
    app.run()
            
