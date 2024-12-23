import json
import requests

json_file_path = '65513757cf7194001ae53caa.json'
# url = 'https://s-ai.clickster.io/predict?lpg_group_id=65513757cf7194001ae53caa'
url = 'http://127.0.0.1:5000/predict?lpg_group_id=65513757cf7194001ae53caa'

with open(json_file_path, 'r', encoding='latin1') as file:
    json_data_list = json.load(file)

total_matches = 0
total_mismatches = 0

for index, json_data in enumerate(json_data_list, 1):
    try:
        response = requests.post(url, json=json_data)

        if response.status_code == 200:
            print(f"POST request {index} successful")

            if 'landing_pages_group' in json_data and 'landingPages' in json_data['landing_pages_group']:
                expected_id = json_data['landing_pages_group']['landingPages'][0].get('_id', '')
            else:
                expected_id = ''

            server_response = response.json()
            landing_page_id = server_response.get('landing_page_id', '')

            if expected_id == landing_page_id:
                print(f"Response {index} matches the expected _id and landing_page_id: {expected_id}")
                total_matches += 1
            else:
                print(f"Response {index} does not match the expected _id not landing_page_id: {expected_id} not {landing_page_id}")
                total_mismatches += 1

        else:
            print(f"POST request {index} failed with status code {response.status_code}")

    except Exception as e:
        print(f"An error occurred for request {index}: {e}")

print(f"Total matches: {total_matches}")
print(f"Total mismatches: {total_mismatches}")

