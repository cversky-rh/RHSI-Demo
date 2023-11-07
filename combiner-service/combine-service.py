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
            address = line.strip()
            urls.append(address)
except FileNotFoundError as e:
    print(f"Error: {e}")

print("IP addresses read from the file:", urls)

app = Flask(__name__)
CORS(app)

@app.route('/combined_get')
def combined_get():
    report_time = 0
    elapsed_time = 0
    all_states = []

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            data_json = response.json()
            report_time = data_json['report_time']
            elapsed_time += data_json['elapsed_time_us']
            states = data_json['states']
            all_states.extend(states)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {url}: {e}")
        except KeyError as e:
            print(f"Error processing data from {url}: Missing key {e}")

    new_data = {
        "report_time": report_time,
        "elapsed_time_us": elapsed_time,
        "states": all_states
    }

    return new_data

if __name__ == '__main__':
    app.run()
